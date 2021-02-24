from flask import Flask, render_template, request
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import moviepy.editor as mp
import speech_recognition as sr
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
def sumup(text):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text)
    freq_table = dict()
    for word in words:
        word = word.lower()
        if word in stop_words:
            continue
        if word in freq_table:
            freq_table[word] += 1
        else:
            freq_table[word] = 1
    sentences = sent_tokenize(text)
    sentence_value = dict()
    for sentence in sentences:
        for word, freq in freq_table.items():
            if word in sentence.lower():
                if sentence in sentence_value:
                    sentence_value[sentence] += freq
                else:
                    sentence_value[sentence] = freq
    sum_values = 0
    for sentence in sentence_value:
        sum_values += sentence_value[sentence]
    average = int(sum_values / len(sentence_value))
    summary = ''
    for sentence in sentences:
        if (sentence in sentence_value) and (sentence_value[sentence] > (1.2 * average)):
            summary += " " + sentence
    return summary


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        txt = request.form.get("text")
        if txt != "":
            url_content = sumup(txt)
        else:
            f1 = request.files['vid']
            f1.save(secure_filename(f1.filename))
            clip = mp.VideoFileClip(f1.filename)
            clip.audio.write_audiofile(r"out.wav")
            r = sr.Recognizer()
            with sr.AudioFile('out.wav') as source:
                audio_text = r.listen(source)
            txt = r.recognize_google(audio_text)
            os.remove('out.wav')
            # os.remove(f1.filename)
            print(txt)
            url_content = sumup(txt)
        return url_content
    return render_template("summarizer.html")


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    header['Access-Control-Allow-Methods'] = 'OPTIONS, HEAD, GET, POST, DELETE, PUT'
    return response


if __name__ == "__main__":
    app.run(debug=True)

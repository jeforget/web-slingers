FROM python:3.8
ENV HOME /root
WORKDIR /root
COPY . .
RUN pip install flask
RUN pip install Flask-Limiter
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python3", "-u", "app.py", "flask"]

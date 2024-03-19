FROM python:3.8
ENV HOME /root
WORKDIR /root
COPY . .
RUN pip install flask
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python3", "-u", "app.py", "flask"]

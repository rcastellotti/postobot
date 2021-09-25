FROM python:latest

WORKDIR /bot
ADD *.py  requirements.txt /bot/
RUN apt update && apt upgrade && apt install -y firefox-esr
RUN sh -c "wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz \ 
            && tar -x geckodriver -zf geckodriver-v0.30.0-linux64.tar.gz -O > /usr/bin/geckodriver \
            && chmod +x /usr/bin/geckodriver \
            && rm geckodriver-v0.30.0-linux64.tar.gz"
RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]



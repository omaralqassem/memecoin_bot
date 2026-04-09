# 1. Use Python
FROM python:3.10-slim

# 2. Set up a safe user (Hugging Face requirement)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

# 3. Copy your requirements and install them
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy all your bot files into the cloud
COPY --chown=user . .

# 5. Start the bot!
CMD ["python", "engine.py"]
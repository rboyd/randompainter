FROM python:3

WORKDIR /usr/src/app

#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install flet --upgrade

COPY paint.py ./
COPY color_picker ./color_picker
#COPY requirements.txt ./
RUN flet publish paint.py


# (Your other Docker instructions, e.g. setting up Python, copying 'dist' directory, etc.)

# Copy the custom server script to the root of the image
COPY always_serve_index.py /always_serve_index.py

# Command to run when the container starts
CMD ["python", "/always_serve_index.py"]

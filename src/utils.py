def read_uploaded_file(uploaded_files):
    texts = []

    for uploaded_file in uploaded_files:
        texts.append(
            uploaded_file.read().decode("utf-8")
        )

    return texts
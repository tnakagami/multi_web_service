document.addEventListener('DOMContentLoaded', e => {
    const upload = (uploadFile, textarea) => {
        const insertText = (textarea, text) => {
            const cursorPos      = textarea.selectionStart;
            const last      = textarea.value.length;
            const before   = textarea.value.substr(0, cursorPos);
            const after    = textarea.value.substr(cursorPos, last);
            textarea.value = before + text + after;
        };
        const getCookie = name => {
            if (document.cookie && document.cookie !== '') {
                for (const cookie of document.cookie.split(';')) {
                    const [key, value] = cookie.trim().split('=');
                    if (key === name) {
                        return decodeURIComponent(value);
                    }
                }
            }
        };

        const formData = new FormData();
        formData.append('file', uploadFile);
        fetch(textarea.dataset.url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        }).then(response => {
            return response.json();
        }).then(response => {
            const extension = response.url.split('.').pop().toLowerCase();

            if (['png', 'jpg', 'gif', 'jpeg', 'bmp'].includes(extension)) {
                html = `![](${response.url})`;
            } else {
                html= `[](${response.url})`;
            }

            insertText(textarea, html);

        }).catch(error => {
            console.log(error);
        });
    };

    for (const textarea of document.querySelectorAll('textarea.uploadable')) {
        textarea.addEventListener('dragover', e => {
            e.preventDefault();
        });

        textarea.addEventListener('drop', e => {
            e.preventDefault();
            upload(e.dataTransfer.files[0], textarea);
        });
    }
});

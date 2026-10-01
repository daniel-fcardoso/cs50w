document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".edit-button").forEach(button => {

        button.addEventListener("click", () => {

            const postId = button.dataset.postId;
            const contentElement = document.querySelector(`#content-${postId}`);
            const oldContent = contentElement.innerText;

            const textarea = document.createElement("textarea");
            textarea.className = "form-control mb-2";
            textarea.value = oldContent;
            textarea.rows = 3;

            const saveButton = document.createElement("button");
            saveButton.className = "btn btn-sm btn-success";
            saveButton.innerText = "Save";

            contentElement.replaceWith(textarea);
            button.style.display = "none";

            button.parentElement.insertBefore(
                saveButton,
                button
            );

            saveButton.addEventListener("click", () => {

                const newContent = textarea.value.trim();

                if (!newContent) {
                    alert("Post content cannot be empty.");
                    return;
                }

                fetch(`/posts/${postId}/edit`, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken")
                    },
                    body: JSON.stringify({
                        content: newContent
                    })
                })
                .then(response => response.json())
                .then(data => {

                    if (data.error) {
                        alert(data.error);
                        return;
                    }

                    const newContentElement = document.createElement("p");
                    newContentElement.className = "card-text post-content";
                    newContentElement.id = `content-${postId}`;
                    newContentElement.innerText = data.content;

                    textarea.replaceWith(newContentElement);

                    saveButton.remove();
                    button.style.display = "inline-block";
                });

            });

        });

    });


    document.querySelectorAll(".like-button").forEach(button => {

        button.addEventListener("click", () => {

            const postId = button.dataset.postId;

            fetch(`/posts/${postId}/like`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                }
            })
            .then(response => response.json())
            .then(data => {

                if (data.error) {
                    alert(data.error);
                    return;
                }

                const likesCount = document.querySelector(
                    `#likes-count-${postId}`
                );

                likesCount.innerText = `❤️ ${data.likes_count}`;

                if (data.liked) {
                    button.innerText = "Unlike";
                } else {
                    button.innerText = "Like";
                }

            });

        });

    });

});


function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {

            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + "=")) {

                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;
            }
        }
    }

    return cookieValue;
}

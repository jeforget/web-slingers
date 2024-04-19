$(document).ready(function() {
    var socket = io.connect('http://' + document.domain + ':' + location.port, {transports: ['websocket']});

    console.log('Client-side script has loaded.');

    $('#submit-post').on('click', function() {
        var content = $('#post-content').val().trim();
        console.log('Attempting to post content:', content);
        if (content) {
            socket.emit('create_post', { content: content });
            $('#post-content').val('');
        } else {
            alert('Please enter some text before posting.');
        }
    });

   socket.on('post_created', function(data) {
    console.log('post_created event received:', data);
    if (data.status === 'success') {

        displayMessage(data.message);
        if (data.post && data.post._id && data.post.username && data.post.content) {
            appendNewPost(data.post);
        } else {
            console.error('Received post object does not have the required structure:', data.post);
        }
    } else {
        alert('Error creating post');
    }
});

   function displayMessage(message) {
    $('#message-container').text(message).fadeIn(500).delay(3000).fadeOut(500);
}

    function appendNewPost(post) {
        console.log('Appending new post:', post);

        if (!post || !post._id || !post.username || !post.content) {
            console.error('Post object is missing properties', post);
            return;
        }

        var postHtml = `<div class="post" id="post-${post._id}">
                            <p><strong>${post.username}</strong> posted:</p>
                            <p>${post.content}</p>
                            <button class="like-button" data-post-id="${post._id}">Like</button>
                            <span id="like-count-${post._id}">0</span>
                            <button class="dislike-button" data-post-id="${post._id}">Dislike</button>
                            <span id="dislike-count-${post._id}">0</span>
                        </div>`;
        $('#posts-container').prepend(postHtml); // Changed to prepend to put the post at the top.
    }

    $('.post-section').on('click', '.like-button, .dislike-button', function() {
        var postId = $(this).data('post-id');
        var action = $(this).hasClass('like-button') ? 'like_post' : 'dislike_post';
        console.log(`Emitting event '${action}' for post ID:`, postId);
        socket.emit(action, { post_id: postId });
    });

    socket.on('connect', function() {
        console.log('WebSocket connected!');
    });

    socket.on('like_response', function(data) {
        console.log('like_response received:', data);
        if (data.result === 'success') {
            $('#like-count-' + data.post._id).text(data.total_likes);
        }
    });

    socket.on('dislike_response', function(data) {
        console.log('dislike_response received:', data);
        if (data.result === 'success') {
            $('#dislike-count-' + data.post._id).text(data.total_dislikes);
        }
    });

    socket.on('error', function(data) {
        console.error('Socket error:', data.message);
        alert('An error occurred: ' + data.message); // Added an alert for user-friendly error messages.
    });
});


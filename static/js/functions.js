$(document).ready(function() {
    var socket = io.connect('http://' + document.domain + ':' + location.port, {transports: ['websocket']});

    console.log('Client script has work.');

    $('#submit-post').on('click', function() {
        var content = $('#post-content').val().trim();
        console.log('Try to post message with:', content);
        if (content) {
            socket.emit('create_post', { content: content });
            $('#post-content').val('');
        } else {
            alert('you should enter text before posting.');
        }
    });

   socket.on('post_created', function(data) {
    console.log('post_created received with:', data);
    if (data.status === 'success') {

        displayMessage(data.message);
        if (data.post && data.post._id && data.post.username && data.post.content) {
            makeNewPost(data.post);
        } else {
            console.error('Received post with error structure:', data.post);
        }
    } else {
        alert('Error with post');
    }
});

   function displayMessage(message) {
    $('#message-container').text(message).fadeIn(500).delay(3000).fadeOut(500);
}

    function makeNewPost(post) {
        console.log(' new post with:', post);

        if (!post || !post._id || !post.username || !post.content) {
            console.error('Post object is missing some part', post);
            return;
        }

        var postMessage = `<div class="post" id="post-${post._id}">
                            <p><strong>${post.username}</strong> posted:</p>
                            <img src="static/profilePics/${post.username}profile_photo.jpg" alt="Profile Picture" style="height: 50px; width: 50px;">
                            <p>${post.content}</p>
                            <button class="like-button" data-post-id="${post._id}">Like</button>
                            <span id="like-count-${post._id}">0</span>
                            <button class="dislike-button" data-post-id="${post._id}">Dislike</button>
                            <span id="dislike-count-${post._id}">0</span>
                        </div>`;
        $('#posts-container').prepend(postMessage);
    }

    $('.post-section').on('click', '.like-button, .dislike-button', function() {
        var postId = $(this).data('post-id');
        var action = $(this).hasClass('like-button') ? 'like_post' : 'dislike_post';
        console.log(`event '${action}' for post ID:`, postId);
        socket.emit(action, { post_id: postId });
    });

    socket.on('connect', function() {
        console.log('WebSocket connected!');
    });

  socket.on('like_response', function(data) {
    console.log('like_response received:', data);
    if (data.result === 'success') {

        if (data.post && data.post._id) {
            $('#like-count-' + data.post._id).text(data.total_likes);
        } else {
            console.error('Invalid structure for like_response:', data);
        }
    }
});


   socket.on('dislike_response', function(data) {
    console.log('dislike_response received:', data);
    if (data.result === 'success') {
        if (data.post && data.post._id) {
            $('#dislike-count-' + data.post._id).text(data.total_dislikes);
        } else {
            console.error('Invalid structure for dislike_response:', data);
        }
    }
});


    socket.on('error', function(data) {
        console.error('Socket error:', data.message);
        alert('An error occurred: ' + data.message);
    });
});


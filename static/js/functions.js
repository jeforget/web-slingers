$(document).ready(function() {
    var socket = io.connect('http://' + document.domain + ':' + location.port, {transports: ['websocket']});

    console.log('Client-side script has loaded.');

    // Emit a 'create_post' event when the post button is clicked
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

    // Append a new post to the DOM when a 'post_created' event is received
   socket.on('post_created', function(data) {
    console.log('post_created event received:', data);
    if (data.status === 'success') {
        alert(data.message);
        if (data.post && data.post._id && data.post.username && data.post.content) {
            appendNewPost(data.post);
        } else {
            console.error('Received post object does not have the required structure:', data.post);
        }
    } else {
        alert('Error creating post');
    }
});


    // Define the appendNewPost function in the ready scope
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
        $('.post-section').append(postHtml);
    }

    // Emit a 'like_post' or 'dislike_post' event when the corresponding button is clicked
    $('.post-section').on('click', '.like-button, .dislike-button', function() {
        var postId = $(this).data('post-id');
        var action = $(this).hasClass('like-button') ? 'like_post' : 'dislike_post';
        console.log(`Emitting event '${action}' for post ID:`, postId);
        socket.emit(action, { post_id: postId });
    });

    socket.on('connect', function() {
    console.log('WebSocket connected!');
});

    // Handle 'like_response' and 'dislike_response' events to update like/dislike counts
    socket.on('like_response', function(data) {
        console.log('like_response received:', data);
        if (data.result === 'success') {
            $('#like-count-' + data.post_id).text(data.total_likes);
        }
    });

    socket.on('dislike_response', function(data) {
        console.log('dislike_response received:', data);
        if (data.result === 'success') {
            $('#dislike-count-' + data.post_id).text(data.total_dislikes);
        }
    });

    // Handle error events
    socket.on('error', function(data) {
        console.error('Socket error:', data.message);
    });
});

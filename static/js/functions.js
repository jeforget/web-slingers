function handlePost(postId, action) {

  $.ajax({
    type: "POST",
    url: "/" + action + "_post",
    data: {
      post_id: postId
    },
    success: function(click_response) {

      if (click_response.result === 'success') {

        let Countnum;
        if (action === 'like') {
    Countnum = click_response.total_likes;
} else {
    Countnum = click_response.total_dislikes;
}

        const countIdSelector = "#" + action + "-count-" + postId;


        $(countIdSelector).text(Countnum);
      } else {

        alert(click_response.message);
      }
    },
    error: function() {
      alert('Don\'t swipe votes');
    }
  });
}

// seck
$(document).ready(function() {

  $('.like-button').click(function() {
    const postId = $(this).data('post-id');
    handlePost(postId, 'like');
  });


  $('.dislike-button').click(function() {
    var postId = $(this).data('post-id');
    handlePost(postId, 'dislike');
  });
});

//se
var socket = io.connect('http://' + document.domain + ':' + location.port);

$('.like-button').click(function() {
    var postId = $(this).data('post-id');
    socket.emit('like_post', {post_id: postId});
});

$('.dislike-button').click(function() {
    var postId = $(this).data('post-id');
    socket.emit('dislike_post', {post_id: postId});
});


socket.on('post_created', function(data) {

});

socket.on('like_updated', function(data) {
    $('#like-count-' + data.post_id).text(data.new_like_count);
});

socket.on('dislike_updated', function(data) {
    $('#dislike-count-' + data.post_id).text(data.new_dislike_count);
});

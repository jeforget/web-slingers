function handlePost(postId, action) {

  $.ajax({
    type: "POST",
    url: "/" + action + "_post",
    data: {
      post_id: postId
    },
    success: function(response) {

      if (response.result === 'success') {

        var newCount = action === 'like' ? response.total_likes : response.total_dislikes;
        $("#" + action + "-count-" + postId).text(newCount);
      } else {

        alert(response.message);
      }
    },
    error: function() {

      alert('Don\'t swipe votes');
    }
  });
}


$(document).ready(function() {

  $('.like-button').click(function() {
    var postId = $(this).data('post-id');
    handlePost(postId, 'like');
  });


  $('.dislike-button').click(function() {
    var postId = $(this).data('post-id');
    handlePost(postId, 'dislike');
  });
});



function handlePostInteraction(postId, action) {
  $.ajax({
    type: "POST",
    url: "/" + action + "_post",
    data: {
      post_id: postId
    },
    success: function(response) {
      if (response.result === 'success') {

        $("#"+action+"-count-" + postId).text(action === 'like' ? response.new_likes : response.new_dislikes);
      } else {
        alert(response.message);
      }
    },
    error: function() {
      alert('There was an error processing your request.');
    }
  });
}


$(document).ready(function() {
  $('.like-button').click(function() {
    var postId = $(this).data('post-id');
    handlePostInteraction(postId, 'like');
  });

  $('.dislike-button').click(function() {
    var postId = $(this).data('post-id');
    handlePostInteraction(postId, 'dislike');
  });
});

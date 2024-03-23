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

$(function(formid) {
  
    var job = $('#job');
    //var save = $('#save')
    console.log(formid)
    // list container
    //var listContainer = $('#list');
    //console.log(job);
    $(document).on('submit', formid,function(e){
    //save.on('click', function(e){
      //console.log("MANNAGGIA")
        e.preventDefault();
          $.ajax({
            type: "POST",
            url: 'savejob',
            //url:'{% url "savejob" %}',
            data:{
              //meal: $('#job').val(),
              meal: job.val(),
              //meal: meal,
              csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
              action: 'post'
            },
            success: function(result){
              alert("Success");
            },
            error : function(xhr,errmsg,err) {
              console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
          });
        });
    });
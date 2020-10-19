let fileSelected = 0;

//RESUMABLE JS RELATED FUNCTIONS
//Resumable JS object
var r = new Resumable({
  target:'/api/upload',
  query:{upload_token:'my_token'},
  maxChunkRetries: 2,
  maxFiles: 1,
  prioritizeFirstAndLastChunk: true,
  simultaneousUploads: 4,
  chunkSize: 1 * 1024 * 1024
});

// Resumable.js isn't supported, fall back on a different method
if(!r.support){
	window.alert("Your browser doesn't support Resumable JS")
}

//Assigning browser button for selecting file to upload
r.assignBrowse(document.getElementById('browseButton'));

r.on('fileAdded', function(file, event){
    window.alert("File selected, you can upload now"+r.uniqueIdentifier);
    fileSelected = 1;
  });

r.on('cancel', function(){
  if (confirm('Are you sure you want to cancel the upload?')) {
    var request = $.ajax({
    url: "/api/upload/cancel",
    type: "POST",
    dataType: 'text',
    success: function(data,status,xhr){
      window.alert(data);
    },
    error: function(xhr,status,error){
      window.alert(status);
    }
  });
  }
  });

r.on('fileSuccess', function(file, message){
  fileSelected--;
  $('#status').text("Successfully Uploaded");
  $('#pauseResumeBtn').css("display","none");
  window.alert("Successfully Uploaded File");
  });

r.on('fileError', function(file, message){
  });

r.on('fileProgress', function (file) {
        var progress = Math.floor(file.progress() * 100);
        $('#status').text("Uploading "+progress+"%");
    });

//EVENT RELATED FUNCTIONS
//Baseline Upload Functions
$('#uploadBtn').on('click', function () {
        if (fileSelected > 0) {
            r.upload();
            $('#status').text("Uploading 0%");
            $('#pauseResumeBtn').css("display","");
            $('#stopBtn').css("display","");
        } else {
          window.alert("You haven't selected any file to upload");
        }
        
    });

$('#pauseResumeBtn').on('click', function () {
  let cur_status = $('#pauseResumeBtn').attr('cur_status');
  if(cur_status=='pause'){
    $('#pauseResumeBtn').attr('cur_status','resume');
    $('#pauseResumeBtn').text('Resume');
    r.pause();
  }
  else if(cur_status=='resume'){
    $('#pauseResumeBtn').attr('cur_status','pause');
    $('#pauseResumeBtn').text('Pause');
    r.upload();
  }
});

$('#stopBtn').on('click', function () {
  r.cancel();
  
});



//Export Functions
$('#exportDownloadBtn').on('click', function () {
  window.location.href = "api/export/new"
});

$('#exportToggleStatusBtn').on('click', function () {
  var cur_status = $('#exportToggleStatusBtn').attr('cur_status');
  if(cur_status=='pause')
  {
    $('#exportToggleStatusBtn').attr('cur_status','resume');
    $('#exportToggleStatusBtn').text('Resume');
  }
  else{
    $('#exportToggleStatusBtn').attr('cur_status','pause');
    $('#exportToggleStatusBtn').text('Pause');
  }
  var request = $.ajax({
    url: "/api/export/status/toggle",
    type: "PUT",
    dataType: 'text',
    success: function(data,status,xhr){
      window.alert(data);
    },
    error: function(xhr,status,error){
      window.alert(status);
    }
  });
});

$('#exportCancelBtn').on('click', function () {
  var request = $.ajax({
    url: "/api/export/cancel",
    type: "PUT",
    dataType: 'text',
    success: function(data,status,xhr){
      window.alert("Cancelled Successfully");
    },
    error: function(xhr,status,error){
      window.alert(status);
    }
  });
});

//Bulk Teams Functions
$('#createTeamBtn').on('click', function () {
  var no_of_teams = parseInt($('#no_of_teams').val());
  var request = $.ajax({
    url: "/api/bulk_teams/create",
    type: "GET",
    dataType: 'text',
    data: {
      'no_of_teams':no_of_teams
    },
    success: function(data,status,xhr){
      window.alert(data);
    },
    error: function(xhr,status,error){
      window.alert(status);
    }
  });
});

$('#toggleStatusTeamBtn').on('click', function () {
  var cur_status = $('#toggleStatusTeamBtn').attr('cur_status');
  if(cur_status=='pause')
  {
    $('#toggleStatusTeamBtn').attr('cur_status','resume');
    $('#toggleStatusTeamBtn').text('Resume');
  }
  else{
    $('#toggleStatusTeamBtn').attr('cur_status','pause');
    $('#toggleStatusTeamBtn').text('Pause');
  }
  var request = $.ajax({
    url: "/api/bulk_teams/status/toggle",
    type: "PUT",
    dataType: 'text',
    success: function(data,status,xhr){
      window.alert(data);
    },
    error: function(xhr,status,error){
      window.alert(status);
    }
  });
});

$('#cancelTeamBtn').on('click', function () {
  var request = $.ajax({
    url: "/api/bulk_teams/cancel",
    type: "PUT",
    dataType: 'text',
    success: function(data,status,xhr){
      window.alert(data);
    },
    error: function(xhr,status,error){
      window.alert(status);
    }
  });
});
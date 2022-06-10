function initComponents(compartmentId, projectId) {
  // Load the list of project in the compartment.
  $("#compartments").change(function() {
    var ocid = $("#compartments").val();
    $.getJSON("/projects/" + ocid, function(data) {
      var projectSelector = $("#projects");
      projectSelector.empty();
      if (!projectId) {
        projectSelector.append('<option value="" selected="selected">Select Project</option>');
      }
      data.projects.forEach(element => {
        if (element.ocid === projectId) {
          projectSelector.append('<option value="' + element.ocid + '" selected>' + element.display_name + '</option>');
        } else {
          projectSelector.append('<option value="' + element.ocid + '">' + element.display_name + '</option>');
        }
      });
    })
  })
  // Trigger the compartment change callback to load the list of projects.
  $("#compartments").change();
  // Refresh the page to see jobs when project is changed.
  $("#projects").change(function() {
    projectId = $("#projects").val();
    compartmentId = $("#compartments").val();
    window.location.href = "/" + compartmentId + "/" + projectId;
  });
}

function updateLogs(ocid, outputDiv) {
  console.log("Getting logs for " + ocid);
  // Get the most recent logs of each job
  $.getJSON("/logs/" + ocid, function (data) {
    // console.log($("#" + ocid));
    outputDiv.html(data.logs.join("<br />"));
    // Scroll to the bottom
    outputDiv.scrollTop(outputDiv[0].scrollHeight);
    parent = outputDiv.closest(".card");
    statusText = parent.find(".run-status");
    statusText.text(data.status);
    statusDetailsText = parent.find(".run-status-details");
    if (data.statusDetails !== null) {
      statusDetailsText.text(data.status + " - " + data.statusDetails);
    } else {
      statusDetailsText.text(data.status);
    }

    if (data.stopped !== true) {
      // Job is running
      setTimeout(function () {
        updateLogs(ocid, outputDiv)
      }, 20000);
      setCardStyle(parent, "border-primary");
      statusText.addClass("text-primary");
      parent.find(".card-header").addClass("bg-primary bg-opacity-10");
    } else {
      // Job terminated
      if (data.status === "SUCCEEDED") {
        setCardStyle(parent, "border-success");
        statusText.addClass("text-success");
        parent.find(".card-header").addClass("bg-success bg-opacity-10");
      } else if (data.status === "FAILED") {
        setCardStyle(parent, "border-danger");
        statusText.addClass("text-danger");
        parent.find(".card-header").addClass("bg-danger bg-opacity-10");
      }
    }
  })
}

function setCardStyle(card, newClass) {
  card.removeClass("border-primary");
  card.addClass(newClass);
}

function deleteJob(ocid) {
  $.getJSON("/delete/" + ocid, function (data) {
    console.log("Deleting " + ocid);
    if (data.error === null) {
      $("." + ocid.replace(/\./g, "")).remove();
    } else {
      alert(data.error);
    }

  });
}

function loadJobs(compartmentId, projectId) {
  var limit = $("#job-number-limit").text();
  var existing_jobs = $("#dashboard-jobs .accordion-item .job-ocid").map(function () {
    return $(this).text();
  }).get();
  $.getJSON("/jobs/" + compartmentId + "/" + projectId + "?limit=" + limit, function (data) {
    data.jobs.reverse().forEach(job => {
      if (existing_jobs.indexOf(job.ocid) < 0) {
        console.log("Loading new job: " + job.ocid);
        $("#dashboard-jobs").prepend(job.html);
        loadJobRuns(job.ocid);
      }
    });
  });
  // Reload the list of jobs every 20 seconds.
  setTimeout(function () {
    loadJobs(compartmentId, projectId);
  }, 20000);
}

function loadJobRuns(job_ocid) {
  var jobSelector = "#" + job_ocid.replaceAll(".", "") + "-body";
  var jobRow = $(jobSelector).find(".row").append("");
  console.log("Loading job runs for job OCID: " + job_ocid);
  $.getJSON("/job_runs/" + job_ocid, function (data) {
    data.runs.forEach(run => {
      jobRow.append(run.html);
      // Load logs.
      var jobRunSelector = "#" + run.ocid.replaceAll(".", "")
      $(jobRunSelector + " .run-monitor").each(function () {
        var ocid = this.id;
        var outputDiv = $(this).find(".card-body");
        updateLogs(ocid, outputDiv);
      });
    });
  });
}

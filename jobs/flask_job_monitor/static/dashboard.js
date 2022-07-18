const JOB_CHECKING_INTERVAL = 20000;
const LOG_CHECKING_INTERVAL = 20000;
const RUN_CHECKING_INTERVAL = 30000;
var jobRunChecking = {};

function initComponents(compartmentId, projectId) {
  // Load the list of project in the compartment.
  $("#compartments").change(function() {
    var ocid = $("#compartments").val();
    var serviceEndpoint = $("#service-endpoint").text();
    $.getJSON("/projects/" + ocid + "?endpoint=" + serviceEndpoint, function(data) {
      var projectSelector = $("#projects");
      projectSelector.empty();
      console.log(projectId);
      if (projectId == "None" || projectId == "all") {
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
  if (compartmentId) $("#compartments").change();
  // Refresh the page to see jobs when project is changed.
  $("#projects").change(function() {
    projectId = $("#projects").val();
    compartmentId = $("#compartments").val();
    window.location.href = "/" + compartmentId + "/" + projectId + window.location.search;
  });
}

function updateLogs(ocid, outputDiv) {
  // console.log("Getting logs for " + ocid);
  // Get the most recent logs of each job
  $.getJSON("/logs/" + ocid, function (data) {
    // console.log($("#" + ocid));
    var ansiUp = new AnsiUp;
    var htmlLogs = ansiUp.ansi_to_html(data.logs.join("\n"));
    outputDiv.html(htmlLogs);
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
      }, LOG_CHECKING_INTERVAL);
      setCardStyle(parent, "border-primary");
      statusText.addClass("text-primary");
      parent.find(".card-header").addClass("bg-primary bg-opacity-10");
    } else {
      // Job terminated
      if (data.status === "SUCCEEDED") {
        setCardStyle(parent, "border-success");
        statusText.addClass("text-success");
        parent.find(".card-header").addClass("bg-success text-success bg-opacity-10");
      } else if (data.status === "FAILED") {
        setCardStyle(parent, "border-danger");
        statusText.addClass("text-danger");
        parent.find(".card-header").addClass("bg-danger text-danger bg-opacity-10");
      }
    }
  })
}

function setCardStyle(card, borderClass) {
  card.removeClass("border-primary");
  card.addClass(borderClass);
}

function deleteJob(ocid) {
  var serviceEndpoint = $("#service-endpoint").text();
  $.getJSON("/delete/" + ocid + "?endpoint=" + serviceEndpoint, function (data) {
    console.log("Deleting " + ocid);
    if (data.error === null) {
      $("#" + ocid.replace(/\./g, "")).remove();
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
  var serviceEndpoint = $("#service-endpoint").text();
  var apiEndpoint = "/jobs/" + compartmentId + "/" + projectId + "?limit=" + limit + "&endpoint=" + serviceEndpoint;

  $.getJSON(apiEndpoint, function (data) {
    var timestampDiv = $("#dashboard-jobs").find(".job-timestamp:first");
    var timestamp = 0;
    var jobs = data.jobs;
    if (jobs.length === 0) {
      // Wait for the projects dropdown to be populated so that we can get the project name.
      setTimeout(() => {
        var compartmentName = $("#compartments option[value='" + compartmentId + "']").text();
        var projectName = $("#projects option[value='" + projectId + "']").text();
        console.log("No job found in compartment: " + compartmentId + ", project: " + projectId);
        toastMessage("No Job", "There is no job in " + compartmentName + "/" + projectName);
        }, 2000);
      return;
    }
    var prepended = false;
    if (timestampDiv.length !== 0) {
      timestamp = parseFloat(timestampDiv.text())
      jobs = jobs.reverse();
    }
    // Add jobs based on the time created
    jobs.forEach(job => {
      if (existing_jobs.indexOf(job.ocid) < 0 && job.time_created > timestamp) {
        console.log("Loading job: " + job.ocid);
        if (timestamp > 0) {
          $("#dashboard-jobs").prepend(job.html);
          prepended = true;
        } else {
          $("#dashboard-jobs").append(job.html);
        }
        // Load job runs only when the accordion is opened.
        $('#' + job.ocid.replaceAll(".", "")).on('shown.bs.collapse', function () {
          loadJobRuns(job.ocid);
        })

      }
    });
    // Open the first accordion in the page
    // If user is opening loading the jobs for the first time or new job added recently
    if (existing_jobs.length === 0 || prepended) {
      new bootstrap.Collapse(
        document.getElementsByClassName('accordion-collapse collapse')[0],
        {toggle: true}
      );
    }

  });
  // Reload the list of jobs every 20 seconds.
  setTimeout(function () {
    loadJobs(compartmentId, projectId);
  }, JOB_CHECKING_INTERVAL);
}

function loadJobRuns(job_ocid) {
  const RUNNING = "running"
  // Avoid running the same function twice
  if (typeof(jobRunChecking[job_ocid]) === RUNNING) return;
  if (typeof(jobRunChecking[job_ocid]) === "number") clearTimeout(jobRunChecking[job_ocid]);
  jobRunChecking[job_ocid] = RUNNING;

  // Load job runs only if the accordion is opened.
  var jobAccordion = $("#" + job_ocid.replaceAll(".", "") + "-body");
  if (!jobAccordion.hasClass("show")) return;

  var jobRow = jobAccordion.find(".row");
  if (jobRow.length === 0) return;
  jobRow.append("");
  var serviceEndpoint = $("#service-endpoint").text();
  console.log("Loading job runs for job OCID: " + job_ocid);
  $.getJSON("/job_runs/" + job_ocid + "?endpoint=" + serviceEndpoint, function (data) {
    if (jobRow.find(".col-xxl-4").length === 0) jobRow.empty();
    if (data.runs.length === 0) jobRow.text("No Job Run Found.");
    data.runs.reverse().forEach(run => {
      var jobRunSelector = "#" + run.ocid.replaceAll(".", "");
      runDiv = jobRow.find(jobRunSelector);
      if (runDiv.length === 0) {
        console.log("Adding job run: " + run.ocid);
        jobRow.prepend(run.html);
        runDiv = jobRow.find(jobRunSelector);
        runDiv.find("code").each(function() {
          hljs.highlightElement(this);
        })

        // Load logs.
        $(jobRunSelector + " .run-monitor").each(function () {
          var ocid = this.id;
          var outputDiv = $(this).find(".card-body pre");
          updateLogs(ocid, outputDiv);
        });
      }
    });
  });

  jobRunChecking[job_ocid] = setTimeout(function() {
    loadJobRuns(job_ocid);
    // Check if there is new job run for the job in about 30 seconds.
    // Add a random number to the time interval so that not all requests are send at the same time.
  }, RUN_CHECKING_INTERVAL);
}

function toastMessage(title, message, time) {
  var template = $("#toast-template");
  var toastDiv = template.clone();
  toastDiv.find(".q-toast-title").text(title);
  toastDiv.find(".q-toast-body").text(message);
  if (time !== undefined) toastDiv.find(".q-toast-time").text(time);
  toastDiv.appendTo(template.parent());
  var toast = new bootstrap.Toast(toastDiv);
  toast.show();
}

function downloadLogs(jobRunId) {
  var logs = $("#" + jobRunId.replaceAll(".", "\\.")).find("pre").text();
  var filename = "logs-" + jobRunId + ".log";
  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(logs));
  element.setAttribute('download', filename);
  element.style.display = 'none';
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}
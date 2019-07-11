// Function to enable bootstrap tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

// Function to update the file uploader with the file name and then to reveal the submit button.
$(".custom-file-input").on("change", function () {
    var fileName = $(this).val().split("\\").pop();
    $(this).siblings(".custom-file-label").addClass("selected").html(fileName);

    // Reveal the submit button
    var x = document.getElementById("submit");
    if (x.style.display === "none") {
        x.style.display = "block";
    }
});

// function to send annotations and their IDs back to python to be stored in a database
function postAnnotation(rec_id, annotation){
    $.post( "/updateModel", {
        rec_id: rec_id,
        classification: annotation
    });
};

// gather the user's selected annotation and update the UI with the next article.
function updateArticle(response, rec_index) {

    if (rec_index < response.length) {

        // Update article body text
        d3.select("#articleBody").text(response[rec_index]["XOM Description"]);

        // Event listeners for classification selections
        d3.select("#classA").on("click", function () {

            // JS object to hold the ID and annotation
            anno = { SRQ: response[rec_index]["Service Request Number"], classification: "Not Severe" }

            // call function that will make an AJAX POST request to push annotation to the database
            postAnnotation(anno['SRQ'], anno['classification']);

            // Increment the record index and re-run this function to annotate the next article
            updateArticle(response, rec_index + 1);
        });

        // Replicate for each classification listener

        d3.select("#classB").on("click", function () {
            anno = { SRQ: response[rec_index]["Service Request Number"], classification: "Somewhat Severe" }
            postAnnotation(anno['SRQ'], anno['classification']);
            updateArticle(response, rec_index + 1);
        });
        d3.select("#classC").on("click", function () {
            anno = { SRQ: response[rec_index]["Service Request Number"], classification: "Severe" }
            postAnnotation(anno['SRQ'], anno['classification']);
            updateArticle(response, rec_index + 1);
        });
        d3.select("#classD").on("click", function () {
            anno = { SRQ: response[rec_index]["Service Request Number"], classification: "Very Severe" }
            postAnnotation(anno['SRQ'], anno['classification']);
            updateArticle(response, rec_index + 1);
        });

    }
    else {
        // All articles have been annotated
        d3.select("#articleBody").text("No more articles to annotate!");
        d3.select("#buttonRow").style("display", "none");
    };
}

// function to read the JSON response from Python and trigger another function that iterates within itself until all articles have been annotated. This will need to be updated to allow the user to submit their annotations, or maybe see if we can write each response to the database as we go, depending on the latency.
function displayData() {
    var url = "api/inputData"
    d3.json(url).then(function (response) {

        d3.select("#totalCount").text(response.length);
        updateArticle(response, 0);

    });
}

displayData();
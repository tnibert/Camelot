//https://stackoverflow.com/questions/6142025/dynamically-add-field-to-a-form

$(document).ready(function(){
    form_count = Number($("[name=extra_field_count]").val());
    // get extra form count so we know what index to use for the next item.
    console.log(form_count)

    $("#add-another").click(function() {
        form_count ++;
        console.log(form_count)
        // build elements and append to our forms container
        element = $('<input type="file"/>');
        element.attr('name', 'file_' + form_count);
        $("#forms").append(element);

        element = $('<br>')
        $("#forms").append(element);

        element = $('<input type="text"/>');
        element.attr('name', 'desc_' + form_count);
        $("#forms").append(element);

        element = $('<br>')
        $("#forms").append(element);

        $("[name=extra_field_count]").val(form_count);
        // increment form count so our view knows to populate
        // that many fields for validation
    })
});

/*
<p>
        <label for="id_file">File:</label><br>
        <input type="file" name="file" required id="id_file" />


      </p>
*/

// probably wont use this but keeping for now
function DuplicateIn() {

  var formInvalid = false;
  $('#register_form input').each(function() {
    if ($(this).val() === '') {
      formInvalid = true;
    }
  });

  if (formInvalid)
    alert('One or Two fields are empty. Please fill up all fields');
}
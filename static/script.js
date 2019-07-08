document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.datepicker');
    var instances = M.Datepicker.init(elems, {format: "dd-mmm-yyyy"});
    var selects = document.querySelectorAll('select');
    var selectsInstances = M.FormSelect.init(selects, {});
});
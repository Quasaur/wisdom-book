document.addEventListener('DOMContentLoaded', function() {
    var contentField = document.getElementById('id_content');
    if (contentField) {
        // Initialize CodeMirror
        var editor = CodeMirror.fromTextArea(contentField, {
            mode: "htmlmixed",
            theme: "monokai",
            lineNumbers: true,
            lineWrapping: true,
            viewportMargin: Infinity // Auto-resize height
        });
        
        // Adjust style for the editor container
        editor.getWrapperElement().style.fontSize = "14px";
        editor.getWrapperElement().style.border = "1px solid #ccc";
    }
});

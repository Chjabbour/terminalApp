function formatTextAsCodeBlock() {
    var document = DocumentApp.getActiveDocument();
    var selection = document.getSelection();
    
    if (selection) {
      var rangeElements = selection.getRangeElements();
      for (var i = 0; i < rangeElements.length; i++) {
        var rangeElement = rangeElements[i];
        
        if (rangeElement.getElement().editAsText) {
          var startOffset = rangeElement.getStartOffset();
          var endOffset = rangeElement.getEndOffsetInclusive();
          var textElement = rangeElement.getElement().editAsText();
          
          // Apply monospace font and background color
          textElement.setFontFamily(startOffset, endOffset, 'Courier New');
          textElement.setBackgroundColor(startOffset, endOffset, '#f0f0f0');
        }
      }
    } else {
      DocumentApp.getUi().alert('No text selected.');
    }
  }
  


// To use the script, follow these steps:

// Open your Google document in your browser.
// Click on "Extensions" in the menu bar.
// Click on "Apps Script."
// If you haven't used Google Apps Script with this document before, click on "New script."
// In the script editor, replace the default "Code.gs" content with the provided script.
// You can name the script file "Code.gs" or any other name you prefer, such as "FormatCodeBlock.gs." To rename the file, right-click on the file name in the left pane of the script editor and select "Rename."
// Save the script by clicking the floppy disk icon or pressing Ctrl+S (Cmd+S on macOS).
// To run the script, click on the "Select function" dropdown menu in the toolbar, select the "formatTextAsCodeBlock" function, and then click the triangular "Run" button.

// After following these steps, whenever you select some text in the Google document and run the "formatTextAsCodeBlock" function, the script will apply the specified formatting to the selected text. Please note that this script does not interact with the UI elements as mentioned in your original request. It directly applies the formatting to the selected text when you run the function from the Google Apps Script editor.
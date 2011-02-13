/*global: data, jQuery, _, Showdown, throttle, Cache, tim */

var namespace = "fluffbox",
    maxImageWidth = 500,
    maxImageHeight = 500,
    updateThrottle = 50,
    cacheSaveThrottle = 250,
    markdown = new Showdown.converter(),
    cache = new Cache(namespace),

    // DOM
    //document = window.document,
    fluffElem = jQuery("#fluff"),
    editorElem = jQuery("#editor"),
    previewElem = jQuery("#preview"),
    
    editorVal;


/////


function toHtml(content){
    return markdown.makeHtml(jQuery.trim(content));
}

function sortByTimestamp(a, b){
    return a.timestamp - b.timestamp;
}

// Modified from http://alexking.org/blog/2003/06/02/inserting-at-the-cursor-using-javascript
function insertAtCursor(myField, myValue) {
    var startPos, endPos;

    // IE
    if (document.selection){
        myField.focus();
        sel = document.selection.createRange();
        sel.text = myValue;
    }
    // Others
    else if (myField.selectionStart || myField.selectionStart === 0) {
        startPos = myField.selectionStart;
        endPos = myField.selectionEnd;
        myField.value = myField.value.substring(0, startPos) + myValue + myField.value.substring(endPos, myField.value.length);
    }
    else {
        myField.value += myValue;
    }
    //insertAtCursor(document.formName.fieldName, 'this value');
}


// From http://stackoverflow.com/questions/499126/jquery-set-cursor-position-in-text-area
function setSelectionRange(input, selectionStart, selectionEnd) {
  if (input.setSelectionRange) {
    input.focus();
    input.setSelectionRange(selectionStart, selectionEnd);
  }
  else if (input.createTextRange) {
    var range = input.createTextRange();
    range.collapse(true);
    range.moveEnd('character', selectionEnd);
    range.moveStart('character', selectionStart);
    range.select();
  }
}
function setCaretToPos (input, pos) {
  setSelectionRange(input, pos, pos);
}

function moveCaretToEnd(input){
    setCaretToPos(editorElem[0], input.value.length);
}

function autoHeight(elem){
    elem.css("height", "auto");
    elem.height(elem.attr("scrollHeight"));
}

function removeDataAttr(elem){
    jQuery.each(elem[0].attributes, function(i, attr){
        if (attr.specified && attr.nodeName.indexOf("data-") === 0){
            elem.removeAttr(attr.nodeName);
        }
    });
    return elem;
}


function getData(){
    // TODO: temp
    return data;
}

function updatePreview(){
    previewElem.html(
        toHtml(editorVal)
    );
}
//updatePreview = throttle(updatePreview, previewUpdateThrottle, true);

function saveToCache(){
    cache.set("content", editorVal);
}
saveToCache = throttle(saveToCache, cacheSaveThrottle, true);

function getCachedContent(){
    return cache.get("content");
}

function updateAll(){
    var oldVal = editorVal;
    
    editorVal = editorElem.val();
    if (oldVal !== editorVal){
        autoHeight(editorElem);
        updatePreview();
        saveToCache();
    }
}
updateAll = throttle(updateAll, updateThrottle, true);

function init(){
    var data = getData(),
        fluff = data.fluff.sort(sortByTimestamp);
        
    editorVal = getCachedContent();

    jQuery.each(fluff, function(i, lint){
        jQuery.each(lint.assets, function(i, asset){
            lint.assets[i].content = tim("image", asset);
        }); 
    });

    fluffElem
        .html(
            tim("fluff", data)
        )
        .delegate("[draggable]", "dragstart",function(e){
            _(e);
            var dataTransfer = e.originalEvent.dataTransfer,
                elem = jQuery(this),
                dropContent = elem.attr("data-drop"),
                dropElem, dropNode, width, height, reduction;
                
            if (!dropContent){
                dropElem = elem.clone()
                    .removeAttr("draggable");
                    
                dropNode = dropElem[0];
                removeDataAttr(dropElem);
            
                if (dropNode.nodeName === "IMG"){
                    width = dropNode.width;
                    height = dropNode.height;
                    
                    if (width > maxImageWidth){
                        reduction = maxImageWidth / width;
                        width = maxImageWidth;
                        height = Math.round(height * reduction);
                    }
                    if (height > maxImageHeight){
                        reduction = maxImageHeight / height;
                        height = maxImageHeight;
                        width = Math.round(width * reduction);
                    }
                
                    dropElem
                        .attr("width", width)
                        .attr("height", height);
                }
                    
                dropContent = dropElem.outerHTML();
            }

            dataTransfer.effectAllowed = "copy";
            dataTransfer.setData("text/html", dropContent);
        })
        .find("img").attr("draggable", true);
            
    editorElem
        .bind({
            cut: updateAll,
            paste: updateAll,
            keyup: updateAll,
            change: updateAll
        })
        
        // DnD modified from http://html5rocks.com/tutorials/dnd/basics/
        .bind("dragover", function(e){
            var dataTransfer = e.originalEvent.dataTransfer;
        
            if (e.preventDefault) {
                e.preventDefault(); // Necessary. Allows us to drop.
            }
            dataTransfer.dropEffect = "copy";
            return false;
        })
        .bind("drop", function(e){
            _(event);
            var dataTransfer = e.originalEvent.dataTransfer;
            
            if (e.stopPropagation) {
                e.stopPropagation(); // stops the browser from redirecting.
            }

            insertAtCursor(editorElem[0], dataTransfer.getData('text/html'));
            
            updateAll();
            editorElem.focus();

            return false;
        });
 
        
        // TODO: restore from localStorage, and if populated, then run this
        // moveCaretToEnd(editorElem[0]); editorElem.blur()
        
        
        /* TODO: add settings:
            * inputs for max width, height, img as markdown/html
            * store in localStorage
        */
    if (editorVal){
        editorElem.val(editorVal);
        autoHeight(editorElem);
        updatePreview();
    }
}

init();

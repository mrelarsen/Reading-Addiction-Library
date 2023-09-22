import { loadToggle } from "../../libraries/methods";

globalThis.toggleLoadBar = toggleLoadBar;

function toggleLoadBar(toggle) {
  loadToggle(toggle);
}

var currentViewId = null;
var currentLabel = null;
var currentSection = null;

document.on("closerequest", function (_) {
  Window.this.xcall("shutdown");
});

function selectView(viewId) {
  if (currentLabel != null) {
    currentLabel.state.checked = false;
    currentSection.state.checked = false;
  }

  currentSection = document.$(`.section#${viewId}`);
  currentSection.state.checked = true;
  currentLabel = document.$(`#tabs > label#${viewId}_tab`);
  currentLabel.state.checked = true;
  currentViewId = viewId;
}

document.on("click", "#tabs>label", (_, element) => {
  const viewId = element.attributes["id"].substring(
    0,
    element.attributes["id"].length - 4
  );
  selectView(viewId);
});

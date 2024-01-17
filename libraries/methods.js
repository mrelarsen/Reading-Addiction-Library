globalThis.appendOn = appendOn;
globalThis.replaceLast = replaceLast;
globalThis.replaceId = replaceId;
globalThis.scrollTo = scrollTo;
globalThis.scrollToCenterOf = scrollToCenterOf;
globalThis.onClick = onClick;
globalThis.loadToggle = loadAndCallToggle;

export function loadAndCallToggle(check, handler, methodName, params) {
  loadToggle(check);
  if (handler && methodName) {
    Window.this.xcall("call_handler", handler, methodName, params || []);
  }
}

export function appendOn(selector, content) {
  document.querySelector(selector).append(content);
}

export function replaceLast(selector, content) {
  const divs = document.querySelectorAll(`${selector} > div`);
  if (divs.length > 0) {
    divs[divs.length - 1].remove();
    document.querySelector(selector).append(content);
  }
}

export function replaceId(id, content) {
  const selector = "#" + id;
  const element = document.querySelector(selector);
  element.innerHTML = content;
}

export function scrollTo(selector, behavior = "smooth", block = "start") {
  document.$(selector).scrollIntoView({
    behavior: behavior,
    block: block,
  });
}

export function scrollToCenterOf(
  selector,
  from = 0.5,
  to = 0.5,
  elementOffset = 0.5
) {
  const element = document.$(selector);
  const main = element.$p(".scroll-parent");
  const elementBox = element.box("border", main); // Rect, relative to main
  const posRelToMain = elementBox.origin; // Point
  const posInMainContent = posRelToMain + main.scrollPosition; // the above, adjusted to main content
  const mainSize = main.box("client").size;
  const mainPosition = main.scrollPosition; // the above, adjusted to main content
  const fromPosition =
    posInMainContent - mainSize * from + elementBox.size * elementOffset;
  const currentPosition = mainPosition + elementBox.size * elementOffset;
  const toPosition =
    posInMainContent - mainSize * to + elementBox.size * elementOffset;
  if (currentPosition.y < fromPosition.y || currentPosition.y > toPosition.y) {
    main.scrollTo({
      left: toPosition.x,
      top: toPosition.y,
      behavior: "smooth",
    });
  }
}

export function showProps(obj, objName) {
  let result = "";
  Object.keys(obj).forEach((i) => {
    result += `${objName}.${i} = ${obj[i]}\n`;
  });
  console.log(result);
}

export function onClick(pairs) {
  pairs.forEach((pair) => {
    document.on("click", pair[0], pair[1]);
  });
}

export function loadToggle(check) {
  const loaders = document.$$(".loader");
  // console.log(`${loaders.length} loaders set to ${check}`);
  loaders.forEach((loader) => (loader.state.checked = check));
}

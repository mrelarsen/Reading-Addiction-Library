globalThis.appendOn = appendOn;
globalThis.replaceLast = replaceLast;
globalThis.replaceId = replaceId;
globalThis.scrollTo = scrollTo;
globalThis.scrollToIn = scrollToIn;
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

export function scrollToIn(
  containerSelector,
  elementSelector,
  behavior = "smooth",
  block = "start"
) {
  const element = document.$(elementSelector);
  const container = document.$(containerSelector);
  // const container = element.parentNode;
  console.log(
    "container",
    container.scrollHeight,
    container.offsetTop,
    container.clientTop
  );
  console.log("element", element.offsetTop, element.clientTop);
  container.scrollTo(0, -element.offsetTop, false, true);
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

globalThis.appendOn = appendOn;
globalThis.replaceLast = replaceLast;
globalThis.replaceId = replaceId;
globalThis.scrollTo = scrollTo;
globalThis.scrollLineToTop = scrollLineToTop;
globalThis.scrollToCenterOf = scrollToCenterOf;
globalThis.scrollLineToCenter = scrollLineToCenter;
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
  if (element.innerHTML.includes("&nbsp;"))
    element.innerHTML = element.innerHTML.replaceAll("&nbsp;", " ");
}

export function scrollTo(selector, behavior = "smooth", block = "start") {
  document.$(selector).scrollIntoView({
    behavior: behavior,
    block: block,
  });
}

export function scrollLineToTop(lineNumber) {
  const element = document.$(`#line-${lineNumber.toString().padStart(5, "0")}`);
  if (!element) {
    console.warn(
      "Cannot scroll, could not find element to center on:",
      selector
    );
    return;
  }
  const main = element.$p(".scroll-parent");
  main.scrollTo({
    left: 0,
    top: 0,
    behavior: "smooth",
  });
}

export function scrollToCenterOf(
  selector,
  from = 0.5,
  to = 0.5,
  elementOffset = 0.5
) {
  const element = document.$(selector);
  if (!element) {
    console.warn(
      "Cannot scroll, could not find element to center on:",
      selector
    );
    return;
  }
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
      top: Math.max(Math.min(toPosition.y, main.scrollHeight - mainSize.y), 0),
      behavior: "smooth",
    });
  }
}

export function scrollLineToCenter(lineNumber) {
  const from = 0.5,
    to = 0.5,
    elementOffset = 0.5;
  const element = document.$(`#line-${lineNumber.toString().padStart(5, "0")}`);
  if (!element) {
    console.warn(
      "Cannot scroll, could not find element to center on:",
      lineNumber
    );
    return;
  }
  const main = element.$p(".scroll-parent");
  let elementBox = element.box("border", main); // Rect, relative to main
  const nextElement = document.$(
    `#line-${(lineNumber + 1).toString().padStart(5, "0")}`
  );
  if (nextElement && lineNumber > 0) {
    // sporadic inline inline location error
    const previousElement = document.$(
      `#line-${(lineNumber - 1).toString().padStart(5, "0")}`
    );
    const nextBox = nextElement.box("border", main);
    const previousBox = previousElement.box("border", main);
    if (
      elementBox.origin.y > nextBox.origin.y &&
      previousBox.origin.y < nextBox.origin.y
    ) {
      const parentBox = element.parentElement.box("border", main);
      if (
        parentBox.origin.y - 5 < nextBox.origin.y &&
        parentBox.origin.y + 5 > previousBox.origin.y
      ) {
        elementBox = parentBox;
        console.log("Use parent position to scroll");
      }
    }
  }
  let posInMainContent = elementBox.origin + main.scrollPosition;
  if (elementBox.origin.x > 10000) {
    // sporadic location error
    const firstElementBox = document.$(`#line-00000`).box("border", main);
    const secondElementBox = document.$(`#line-00001`).box("border", main);
    const yError =
      secondElementBox.origin.y -
      (secondElementBox.origin.y -
        firstElementBox.origin.y -
        firstElementBox.size.y);
    posInMainContent = new Graphics.Point(
      0,
      elementBox.origin.y - yError * (elementBox.origin.x / firstElementBox.x)
    );
    console.log("Use yError estimat modified position to scroll", yError);
  }
  const mainSize = main.box("client").size;
  const mainPosition = main.scrollPosition; // the above, adjusted to main content
  const fromPosition =
    posInMainContent - mainSize * from + elementBox.size * elementOffset;
  const currentPosition = mainPosition + elementBox.size * elementOffset;
  const toPosition =
    posInMainContent - mainSize * to + elementBox.size * elementOffset;
  if (currentPosition.y < fromPosition.y || currentPosition.y > toPosition.y) {
    main.scrollTo({
      left: 0, //toPosition.x,
      top: Math.max(Math.min(toPosition.y, main.scrollHeight - mainSize.y), 0),
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

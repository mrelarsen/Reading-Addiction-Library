import { VirtualTable } from "../../../../libraries/virtual-list/virtual_table.js";
import { storyColumnMetadata } from "./metadata/story_column_metadata.js";
import { chapterColumnMetadata } from "./metadata/chapter_column_metadata.js";

var stories = document.$("#story_section");

const callStory = (methodName, params) =>
  Window.this.xcall("call_handler", "story_handler", methodName, params || []);

globalThis.setStories = setStories; // put this function into global namespace.
globalThis.setChapters = setChapters; // put this function into global namespace.

var storyId = null;
var chapterId = null;
var storyRow = null;
var chapterRow = null;
var chapterStatus = null;
var storyRowElement = null;
var chapterRowElement = null;
var selectedStories = [];

var storyPicker = stories.$("#story_picker");
var chapterPicker = stories.$("#chapter_picker");

var editStoryBtn;
var mergeStoryBtn;
var editChapterBtn;

document.on("click", "#sts_btn_query_all", () => {
  const stories = callStory("get_stories");
  setStories(stories);
});
document.on("click", "#sts_btn_read_summaries", () =>
  callStory("read_summaries", [storyId])
);
document.on("click", "#mrg_btn_file", () => {
  let fileName = Window.this.selectFile({
    filter: "Database Files (*.db)|*.db;|All Files (*.*)|*.*",
    mode: "open",
    path: URL.toPath(__DIR__ + "../../../python/stories.db"),
  });
  if (fileName) {
    callStory("merge_database", [fileName]);
  }
});

function mergeStories() {
  Window.this.modal({
    url: __DIR__ + "../../modals/merge_stories_modal/merge_stories_modal.htm",
    alignment: -5,
    width: 400,
    height: 350,
    parameters: {
      callStory: callStory,
      stories: selectedStories,
      storyPicker: storyPicker,
    },
  });
}

function editStory() {
  Window.this.modal({
    url: __DIR__ + "../../modals/edit_story_modal/edit_story_modal.htm",
    alignment: -5,
    width: 400,
    height: 350,
    parameters: {
      callStory: callStory,
      storyPicker: storyPicker,
      storyId: storyId,
      storyRow: storyRow,
      storyRowElement: storyRowElement,
    },
  });
}
function editChapter() {
  Window.this.modal({
    url: __DIR__ + "../../modals/edit_chapter_modal/edit_chapter_modal.htm",
    alignment: -5,
    width: 400,
    height: 350,
    parameters: {
      callStory: callStory,
      chapterId: chapterId,
      chapterStatus: chapterStatus,
      chapterRow: chapterRow,
      chapterRowElement: chapterRowElement,
    },
  });
}

function setStories(stories) {
  const parent = storyPicker.parentElement;
  storyPicker.patch(
    <VirtualTable
      data={stories}
      idName={"story_picker"}
      onRowClick={clickStoryRow}
      columnMetadata={storyColumnMetadata}
      toolbar={[
        <button
          class="story_picker_edit_btn dark"
          title="Edit story"
          onclick={editStory}
        >
          <icon class="icon-edit"></icon>
        </button>,
        <button
          class="story_picker_merge_btn dark"
          title="Merges stories"
          onclick={mergeStories}
        >
          <icon class="icon-merge"></icon>
        </button>,
      ]}
    />
  );
  storyPicker = parent.$("#story_picker");
  editStoryBtn = storyPicker.$(".story_picker_edit_btn");
  mergeStoryBtn = storyPicker.$(".story_picker_merge_btn");
  editStoryBtn.state.disabled = true;
  mergeStoryBtn.state.disabled = true;
  if (typeof storyPicker.sortColumnAndUpdateList === "function") {
    const headerElement = storyPicker.$('th[name="created"]');
    storyPicker.sortColumnAndUpdateList(headerElement); // asc
    storyPicker.sortColumnAndUpdateList(headerElement); // desc
  }
}

function clickStoryRow(row, rowElement, selectedRows) {
  console.log(`Clicked row: ${row.name}`);
  const chapterList = callStory("get_chapters", [row["id"]]);
  setChapters(chapterList);
  storyId = row["id"];
  storyRow = row;
  storyRowElement = rowElement;
  selectedStories = selectedRows;
  editStoryBtn.state.disabled = selectedRows.length < 1;
  mergeStoryBtn.state.disabled = selectedRows.length < 2;
}

function setChapters(chapters) {
  const parent = chapterPicker.parentElement;
  chapterPicker.patch(
    <VirtualTable
      data={chapters}
      idName={"chapter_picker"}
      columnMetadata={chapterColumnMetadata}
      onRowClick={clickChapterRow}
      toolbar={[
        <button
          class="chapter_picker_edit_btn dark"
          title="Edit chapter"
          onclick={editChapter}
        >
          <icon class="icon-edit"></icon>
        </button>,
      ]}
    />
  );
  chapterPicker = parent.$("#chapter_picker");
  editChapterBtn = chapterPicker.$(".chapter_picker_edit_btn");
  if (typeof chapterPicker.sortColumnAndUpdateList === "function") {
    const headerElement = chapterPicker.$('th[name="created"]');
    chapterPicker.sortColumnAndUpdateList(headerElement); // asc
    chapterPicker.sortColumnAndUpdateList(headerElement); // desc
    editChapterBtn.state.disabled = true;
  }
}

function clickChapterRow(row, rowElement, selectedRows) {
  console.log(`Clicked row: ${row.name}`);
  callStory("copy_chapter_url", [row["id"]]);
  chapterId = row["id"];
  chapterRow = row;
  chapterStatus = row["status"];
  chapterRowElement = rowElement;
  editChapterBtn.state.disabled = selectedRows.length < 1;
}

import { VirtualTable } from "../../../../libraries/virtual-list/virtual_table.js";
import { storyColumnMetadata } from "../../sections/story_section/metadata/story_column_metadata.js";
const { stories, callStory, storyPicker } = Window.this.parameters;

document.ready = () => {
  const saveBtn = document.$("#btn_story_save");
  saveBtn.on("click", () => merge_stories());
  setStoryDetails();
};

function merge_stories() {
  const storyIds = stories.map((x) => x.id);
  const [deletedIds, story] = callStory("merge_stories", [storyIds]);
  storyPicker.deleteRows(deletedIds);
  storyPicker.overrideRow(story);
  Window.this.close();
}

function setStoryDetails() {
  const inj_stories = document.$("#inj_stories");
  inj_stories.patch(
    <VirtualTable
      data={stories}
      idName={"inj_stories"}
      columnMetadata={storyColumnMetadata}
      hideSettings={true}
    />
  );
}

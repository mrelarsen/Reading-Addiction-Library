import { VirtualTable } from "../../../../libraries/virtual-list/virtual_table.js";
import { storyColumnMetadata } from "../../sections/story_section/metadata/story_column_metadata.js";

export class MergeStoriesModal extends Element {
  stories;
  storyPicker;
  callStory;
  close;

  this(props) {
    this.stories = props.stories;
    this.storyPicker = props.storyPicker;
    this.callStory = props.callStory;
    this.story = this.callStory("get_story", [this.storyId]);
  }

  render() {
    return (
      <div id="modal-content" style="height:*">
        <label id="lbl_story_title">Merge stories</label>
        <br />
        <label>
          Your are attempting to merge these stories into the story with the
          lowest id
        </label>
        <br />
        <VirtualTable
          data={this.stories}
          idName={"inj_stories"}
          columnMetadata={storyColumnMetadata}
          hideSettings={true}
        />
        <button class="dark" id="btn_story_save">
          Save story
        </button>
      </div>
    );
  }

  "on click at #btn_story_save"() {
    const storyIds = this.stories.map((x) => x.id);
    const [deletedIds, story] = this.callStory("merge_stories", [storyIds]);
    this.storyPicker.deleteRows(deletedIds);
    this.storyPicker.overrideRow(story);
    this.close();
  }
}

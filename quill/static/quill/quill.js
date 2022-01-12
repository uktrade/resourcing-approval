class QuillWrapper {
  constructor(containerSelector, quillOptions) {
    // bind methods
    this.getValue = this.getValue.bind(this);
    this.setValue = this.setValue.bind(this);
    this.sync = this.sync.bind(this);

    this.container = document.querySelector(containerSelector);
    this.editor = this.container.querySelector("[data-quill-editor]");
    this.input = this.container.querySelector("[data-quill-input]");

    this.quill = new Quill(this.editor, quillOptions);

    this.setValue(this.input.value);

    this.sync();

    this.quill.on("text-change", this.sync);
  }

  getValue() {
    const delta = this.quill.getContents();

    // Normalize an empty editor to `{}`.
    if (delta.ops.length === 1 && delta.ops[0].insert === "\n") {
      return {};
    }

    // Add a top level `delta` key.
    return { delta };
  }

  setValue(value) {
    const obj = JSON.parse(value || {});

    if (obj.delta) {
      this.quill.setContents(obj.delta);
    } else {
      // This is for handling the delta being at the top level, which is how I
      // originally designed this to work.
      this.quill.setContents(obj);
    }
  }

  sync() {
    this.input.value = JSON.stringify(this.getValue());
  }
}

You can programmatically fill, check the questions and the pre-populated data on the template.
If the template is [properly configured](https://docs.pupil-labs.com/neon/data-collection/templates/#naming-scheme-for-recordings), this allows you to also define the recording name.

??? warning title "Neon Only"

    This functionality is only available for Neon and Neon Companion App >= **2.8.25**.

    If you have an older version, please update your Companion App.

=== "Get the Template"

    ```py linenums="0" title="templates.py"
    --8<-- "examples/simple/templates.py:19:19"
    ```

=== "Get Template's Data"

    ```py linenums="0" title="templates.py"
    --8<-- "examples/simple/templates.py:22:22"
    ```

=== "Post the Template"

    ```py linenums="0" title="templates.py"
    device.post_template_data(questionnaire)
    ```

### Interactively fillout the Template from the Terminal

Check out the full code example below.

<div class="video-container" style="margin: 20px auto; text-align: center;">
<iframe width="800" height="400" src="https://www.youtube-nocookie.com/embed/8jlXjLr1GGE?si=qnEFEnPkHlIp6z7X" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</div>

## Full Code Example

??? example "Check the whole example code here"

    ```py title="templates.py" linenums="1"
    --8<-- "examples/simple/templates.py"
    ```

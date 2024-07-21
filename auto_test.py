#                                           auto_test.py

#                 /* edit only this script if you want to update the steps */
#                 /* in this example i auto test for Spotify apk : searching for songs and run it */

def Auto_test_steps():
    #waiting for every element
    wait = WebDriverWait(driver, 60)

    # Interactions go here
    interact_with_element(wait, By.XPATH, "//android.widget.TextView[@resource-id=\"com.spotify.music:id/bottom_navigation_item_title\" and @text=\"Search\"]", log_queue=log_queue, udid=udid)
    interact_with_element(wait, By.ID, "com.spotify.music:id/find_search_field_text", log_queue=log_queue, udid=udid)
    interact_with_element(wait, By.ID, "com.spotify.music:id/query", action="send_keys", keys="mozart", log_queue=log_queue, udid=udid)
    interact_with_element(wait, By.XPATH, "(//android.view.ViewGroup[@resource-id=\"com.spotify.music:id/row_root\"])[5]", log_queue=log_queue, udid=udid)
    interact_with_element(wait, By.ID, "com.spotify.music:id/button_play_and_pause", log_queue=log_queue, udid=udid)
    #TODO : Complete the test scenario 
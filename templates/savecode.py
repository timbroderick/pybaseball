<!--{% if nl[0].Date == nl[1].Date %}
    <p><strong>On {{ nl[0].Date }},</strong> the Cubs played a doubleheader {% if nl[0].Home_Away == '@' %}at{% else %}at home against{% endif %} the {{ nl[0].Team }}.<br>
     -- In the first game, the Cubs {% if nl[1].WL == 'W' %}won{% elif nl[1].WL == 'W-wo' %}won with a walk-off{% elif nl[1].WL == 'L' %}lost{% elif nl[1].WL == 'L-wo' %}lost after a walk off{% endif %} {{ nl[1].R }} to {{ nl[1].RA }} in {{ nl[1].Inn }} innings. The winning pitcher was {{ nl[1].Win }}, losing pitcher was {{ nl[1].Loss }}. Save: {{ nl[1].Save }}.<br>
     -- In the second game, the Cubs {% if nl[0].WL == 'W' %}won{% elif nl[0].WL == 'W-wo' %}won with a walk-off{% elif nl[0].WL == 'L' %}lost{% elif nl[0].WL == 'L-wo' %}lost after a walk off{% endif %} {{ nl[0].R }} to {{ nl[0].RA }} in {{ nl[0].Inn }} innings. The winning pitcher was {{ nl[0].Win }}, losing pitcher was {{ nl[0].Loss }}. Save: {{ nl[0].Save }}.</p>
    {% else %}
    <p><strong>On {{ nl[0].Date }},</strong> the Cubs {% if nl[0].WL == 'W' %}won a{% elif nl[0].WL == 'W-wo' %}won with a walk-off in a{% elif nl[0].WL == 'L' %}lost a{% elif nl[0].WL == 'L-wo' %}lost after a walk off in a{% endif %} {% if nl[1].DN == 'D' %}day{% else %}night{% endif %} game {% if nl[0].Home_Away == '@' %}at{% else %}at home against{% endif %} the {{ nl[0].Team }}, {{ nl[0].R }} to {{ nl[0].RA }}, in {{ nl[0].Inn }} innings. The winning pitcher was {{ nl[0].Win }}, losing pitcher was {{ nl[0].Loss }}. Save: {{ nl[0].Save }}. </p>
    {% endif %}

{% if nl[2].Date == nl[3].Date %}
    <p><strong>Next scheduled games:</strong> {{ nl[3].Date }}, a doubleheader {% if nl[3].Home_Away == '@' %}at{% else %}at home with{% endif %} the {{ nl[3].Team }}.</p>
    {% else %}
    <p><strong>Next scheduled game:</strong> {{ nl[2].Date }}, {% if nl[2].Home_Away == '@' %}an away game at{% else %}a game at home with{% endif %} the {{ nl[2].Team }}.</p>
    {% endif %}-->


        {% if nl[0].Date == nl[1].Date %}
            <p><strong>On {{ nl[0].Date }},</strong> the Sox played a doubleheader {% if nl[0].Home_Away == '@' %}at{% else %}at home against{% endif %} the {{ nl[0].Team }}.<br>
             -- In the first game, the Sox {% if nl[1].WL == 'W' %}won{% elif nl[1].WL == 'W-wo' %}won with a walk-off{% elif nl[1].WL == 'L' %}lost{% elif nl[1].WL == 'L-wo' %}lost after a walk off{% endif %} {{ nl[1].R }} to {{ nl[1].RA }} in {{ nl[1].Inn }} innings. The winning pitcher was {{ nl[1].Win }}, losing pitcher was {{ nl[1].Loss }}. Save: {{ nl[1].Save }}.<br>
             -- In the second game, the Sox {% if nl[0].WL == 'W' %}won{% elif nl[0].WL == 'W-wo' %}won with a walk-off{% elif nl[0].WL == 'L' %}lost{% elif nl[0].WL == 'L-wo' %}lost after a walk off{% endif %} {{ nl[0].R }} to {{ nl[0].RA }} in {{ nl[0].Inn }} innings. The winning pitcher was {{ nl[0].Win }}, losing pitcher was {{ nl[0].Loss }}. Save: {{ nl[0].Save }}.</p>
            {% else %}
            <p><strong>On {{ nl[0].Date }},</strong> the Sox {% if nl[0].WL == 'W' %}won a{% elif nl[0].WL == 'W-wo' %}won with a walk-off in a{% elif nl[0].WL == 'L' %}lost a{% elif nl[0].WL == 'L-wo' %}lost after a walk off in a{% endif %} {% if nl[1].DN == 'D' %}day{% else %}night{% endif %} game {% if nl[0].Home_Away == '@' %}at{% else %}at home against{% endif %} the {{ nl[0].Team }}, {{ nl[0].R }} to {{ nl[0].RA }}, in {{ nl[0].Inn }} innings. The winning pitcher was {{ nl[0].Win }}, losing pitcher was {{ nl[0].Loss }}. Save: {{ nl[0].Save }}. </p>
            {% endif %}

        <!--{% if nl[2].Date == nl[3].Date %}
            <p><strong>Next scheduled games:</strong> {{ nl[3].Date }}, a doubleheader {% if nl[3].Home_Away == '@' %}at{% else %}at home with{% endif %} the {{ nl[3].Team }}.</p>
            {% else %}
            <p><strong>Next scheduled game:</strong> {{ nl[2].Date }}, {% if nl[2].Home_Away == '@' %}an away game at{% else %}a game at home with{% endif %} the {{ nl[2].Team }}.</p>
            {% endif %}-->

{% extends 'permascroll.base.xhtml.dj.tpl' %}

{%block contents %}
  <div class="document permascroll" id="{{ content_id }}">
    {%block doc-head %}<h1 class="title">{{ doc_title }}</h1> {%endblock%}
    {%block doc-info %}
      {% if doc_info %}
      <table class="docinfo" frame="void" rules="none">
        <col class="docinfo-name" />
        <col class="docinfo-content" />
        <tbody>
            {% for field in doc_info.items %}
          <tr>
            <th class="docinfo-name">{{ field.0 }}:</th>
            <td class="field-body">{{ field.1 }}</td>
           </tr>
          {% endfor %}              
        </tbody>
      </table>
      {% endif %}                  
    {%endblock%}
    {%block doc-body %} {{ doc_body }} {%endblock%}
  </div>
{%endblock%}


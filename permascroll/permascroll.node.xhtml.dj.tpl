{% extends 'permascroll.base.xhtml.dj.tpl' %}

  {%block title %}
  <title>Node {{ doc_info.tumbler.1 }}: {{ doc_title }}</title>
  {%endblock%}

  {%block header %} {%endblock%}

  {%block contents %}
    <div class="document permascroll" id="{{ content_id }}">
      {%block doc-head %}<h1 class="title">{{ doc_title }}</h1> {%endblock%}
      {%block doc-body %} {{ doc_body }} {%endblock%}
    </div>
  {%endblock%}

  {%block footer %}
  <div class="footer"><hr class="footer" />
      {%block doc-info %}
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
      {%endblock%}
  </div> 
  {%endblock%}


{% extends 'permascroll.main.xhtml.dj.tpl' %}
{% block contents %}
   {% ifequal form.method.lower 'get' %}
       <h3 class="permascroll title">{{ title }}</h3>
    {% else %}
       <h3 class="permascroll title">{{ title }} </h3>
    {% endifequal %}

   <form action="{{ form.action }}" method="{{ form.method }}" class="{{ form.classnames }} permascroll">
     <fieldset>

       <legend class="permascroll"><span>{{ form.method.upper }}</span> <span>{{ form.action }}</span></legend>

       {% for field in form.fields %}
         <p class="field model-field">

           {{ field.errors }}

           {% ifequal field.name "srcref" %}
               <label for="{{ field.name }}">&#x2716;</label>
           {% else %}
               {{ field.label_tag }}:
           {% endifequal %}

           {{ field }}

         </p>
       {% endfor %}

       {% for input in form.footer %}
        {% ifequal input.1 '' %}
         <p class="footer field">
             <input type="{{ input.2 }}" value="{{ input.0 }}" />
         </p>
        {% else %}
         <p class="footer field">
               <label for="{{ input.1.lower }}">{{ input.1 }}</label>
             <input type="{{ input.2 }}" name="{{ input.1.lower }}" value="{{ input.0 }}" />
         </p>
        {% endifequal %}
       {% endfor %}

     </fieldset>

     <dl class="docinfo">
       {% for p in doc %}
        <dt>{{ p.0.title }}:</dt>
        {% ifequal p.0 "unid" %}



         <dd>
           <a href="{{ rc.PATH }}/f/{{ p.1  }}">{{ p.1 }}</a>
         </dd>
        {% else %}
         <dd>{{ p.1 }}</dd>
        {% endifequal %}
       {% endfor %}
     </dl>
     
  </form>
{%endblock%}

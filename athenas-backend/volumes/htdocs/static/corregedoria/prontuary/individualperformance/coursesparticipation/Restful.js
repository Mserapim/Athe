Ext._define('corregedoria.prontuary.individualperformance.coursesparticipation.Restful', {
    extend: 'core.Restful',

    resource: 'PRONTUARYDetailCoursesParticipation',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.prontuary.individualperformance.coursesparticipation.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "icons" },
                {type: "string", name: "course" },
                {type: "integer", name: "course_level" },
                {type: "string", name: "course_level_unicode" },
                {type: "integer", name: "workload" },
                {type: "integer", name: "score" },
                {type: "date", name: "date_course", dateFormat: "d/m/Y" },
                {type: "integer", name: "used_edital" },
                {type: "string", name: "used_edital_unicode" },
                {type: "int", name: "validated" },
            ]);

        return this._fields;
    }
});

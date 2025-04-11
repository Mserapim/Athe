 Ext._define('rh.coursecinebrasil.CourseCineBrasilRestful', {
    extend: 'core.Restful',

    resource: 'RHCourseCineBrasil',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.coursecinebrasil.CourseCineBrasilRestful.superclass.getFields.call(this, cfg).concat([
                {type: 'string', name: 'code'},
                {type: 'string', name: 'label'},
            ]);

        return this._fields;
    }
});

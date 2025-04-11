Ext._define('rh.pvf.portalusufruct.Restful', {
    extend: 'core.Restful',

    resource: 'PVFUsufruct',


    getFields: function (cfg) {
        if (!this._fields)
            this._fields = rh.pvf.portalusufruct.Restful.superclass.getFields.call(this, cfg).concat([
                { name: 'created_by', type: 'int', useNull: true },
                { name: 'created_by_unicode', type: 'string' },
                { name: 'modified_by', type: 'int', useNull: true },
                { name: 'modified_by_unicode', type: 'string' },
                { name: 'created_at', type: 'date', dateFormat: 'd/m/Y H:i' },
                { name: 'modified_at', type: 'date', dateFormat: 'd/m/Y H:i' },
                { name: 'status', type: 'int', useNull: true },
                { name: 'status_display', type: 'string' },
                { name: 'start_date', type: 'date', dateFormat: 'd/m/Y' },
                { name: 'end_date', type: 'date', dateFormat: 'd/m/Y' },
                { name: 'end_date_extected', type: 'date', dateFormat: 'd/m/Y' },
                { name: 'days', type: 'int', useNull: true },
                { name: 'from_scale', type: 'bool' },
                { name: 'activity', type: 'int', useNull: true },
                { name: 'activity_unicode', type: 'string' },
                { name: 'employee_unicode', type: 'string' },
                { name: 'authorized_by_unicode', type: 'string' },
                { name: 'authorized_at', type: 'date', dateFormat: 'd/m/Y H:i' },
                { name: 'subtype_usufruct', type: 'string' },
                { name: 'type_activity', type: 'string' },
                { name: 'status_type', type: 'string' },
                { name: 'start_date_acquisition', type: 'date', dateFormat: 'd/m/Y' },
                { name: 'sale_usufruct', type: 'bool'},
                { name: 'acquisition_period', type: 'int', useNull: true },
                { name: 'prev_competence_paid', type:'string'}

            ]);

        return this._fields;
    },

});
   
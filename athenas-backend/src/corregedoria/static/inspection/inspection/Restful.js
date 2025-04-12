Ext._define('corregedoria.inspection.inspection.Restful', {
  extend: 'core.Restful',
  resource: 'INSPECTIONInspection',

    getFields: function(cfg) {
        if(!this._fields) {
          this._fields = corregedoria.inspection.inspection.Restful.superclass.getFields.call(this, cfg).concat([
              {name: "icons"},
              {type: "date", name: "inspection_date_initial", dateFormat: "d/m/Y"},
              {type: "date", name: "inspection_date_final", dateFormat: "d/m/Y"},
              {type: "string", name: "inspection_date_initial_formatted"},
              {type: "string", name: "inspection_date_final_formatted"},
              {type: "string", name: "notice"},
              {type: "string", name: "publication"},
              {type: "int", name: "inspector_general", useNull: true},
              {type: "string", name: "inspector_general_unicode"},
              {type: "int", name: "inspector_prosecutor", useNull: true},
              {type: "int", name: "inspector_prosecutor_pk", useNull: true},
              {type: "string", name: "inspector_prosecutor_unicode"},
              {type: "int", name: "responsible", useNull: true},
              {type: "string", name: "responsible_unicode"},
              {type: "int", name: "atual_employee", useNull: true},
              {type: "int", name: "employee", useNull: true},
              {type: "string", name: "employee_unicode"},
              {type: "int", name: "holder_employee", useNull: true},
              {type: "string", name: "holder_employee_unicode"},
              {type: "string", name: "area_of_action"},
              {type: "string", name: "assignment"},
              {type: "bool", name: "residence"},
              {type: "bool", name: "accumulates"},
              {type: "bool", name: "replacements"},
              {type: "bool", name: "attendance"},
              {type: "bool", name: "teaching"},
              {type: "int", name: "execution_organ", useNull: true},
              {type: "string", name: "execution_organ_unicode"},
              {type: "string", name: "execution_organ_slugify"},
              {type: "date", name: "last_inspection_date", dateFormat: "d/m/Y"},
              {type: "bool", name: "titular_employee"},
              {type: "bool", name: "daily_attendance"},
              {type: "int", name: "days_of_attendance_per_week"},
              {type: "string", name: "attendance_schedule1_inital"},
              {type: "string", name: "attendance_schedule1_final"},
              {type: "string", name: "attendance_schedule2_inital"},
              {type: "string", name: "attendance_schedule2_final"},
              {type: "string", name: "observation"},
              {type: "bool", name: "electoral_applicable_bool"},
              {type: "int", name: "electoral_applicable"},
              {type: "string", name: "electoral_electoralzone"},
              {type: "string", name: "electoral_designation"},
              {type: "string", name: "electoral_initialbiennium"},
              {type: "string", name: "electoral_finalbiennium"},
              {type: "auto", name: "final_score"},
              {type: "bool", name: "inspector_general_bool"},
              {type: "bool", name: "inspector_prosecutor_bool"},
              {type: "int", name: "execution_organ_instance"},
              {type: "auto", name: "operability_score"},
              {type: "auto", name: "promptness_score"},
              {type: "int", name: "inspection_type"},
              {type: "int", name: "structuregeneralstatus"},
              {type: "int", name: "administrativeorganizationgeneralstatus"},
              {type: "int", name: "registration_type"},
          ]);
        }
        return this._fields;
    },

    get_employee: function(values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'get_employee',
                false,
                'POST',
                {
                    params: values,
                    scope: this,
                    callback: function() {
                        core.invokeCallback((cbCallback || {fn: Ext.emptyFn}));
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success)
                            core.invokeCallback((cbSuccess || {fn: Ext.emptyFn}), rst);
                        else
                            core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), rst.message);
                    },
                    failure: function() {
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponível no momento.');
                    }
                }
            )
        );
    },

    get_holder_employee: function(values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'get_holder_employee',
                false,
                'POST',
                {
                    params: values,
                    scope: this,
                    callback: function() {
                        core.invokeCallback((cbCallback || {fn: Ext.emptyFn}));
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success)
                            core.invokeCallback((cbSuccess || {fn: Ext.emptyFn}), rst);
                        else
                            core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), rst.message);
                    },
                    failure: function() {
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponível no momento.');
                    }
                }
            )
        );
    },

    get_area_of_action: function(values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'get_area_of_action',
                false,
                'POST',
                {
                    params: values,
                    scope: this,
                    callback: function() {
                        core.invokeCallback((cbCallback || {fn: Ext.emptyFn}));
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success)
                            core.invokeCallback((cbSuccess || {fn: Ext.emptyFn}), rst);
                        else
                            core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), rst.message);
                    },
                    failure: function() {
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponível no momento.');
                    }
                }
            )
        );
    },

    get_assignment: function(values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'get_assignment',
                false,
                'POST',
                {
                    params: values,
                    scope: this,
                    callback: function() {
                        core.invokeCallback((cbCallback || {fn: Ext.emptyFn}));
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success)
                            core.invokeCallback((cbSuccess || {fn: Ext.emptyFn}), rst);
                        else
                            core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), rst.message);
                    },
                    failure: function() {
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponível no momento.');
                    }
                }
            )
        );
    },

    rendererDocument: function(pk, cbSuccess, cbFailure, cbCallback) {
        var emptyFailure = {
            fn: function(message) {
                Ext.Msg.show({
                    title: 'Buscando documento',
                    msg: message,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        };

        this.doRequest(this.getRoute(
            'renderer_document',
            pk,
            'GET',
            {
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);
                    if(rst.success)
                        core.invokeCallback((cbSuccess || {fn: Ext.emptyFn}), rst.document);
                    else
                        core.invokeCallback((emptyFailure || {fn: Ext.emptyFn}), rst.message);

                },
                failure: function(xhr) {
                    core.invokeCallback((cbFailure || emptyFailure), 'Recurso indisponivel no momento.');
                },
                callback: function() {
                    core.invokeCallback((cbCallback || {fn: Ext.emptyFn}));
                }
            }
        ));
    },

});

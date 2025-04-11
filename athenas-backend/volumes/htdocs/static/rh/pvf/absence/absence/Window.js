Ext._define('rh.pvf.absence.absence.Window', {
    extend: 'rh.pvf.absence.absence.GenericWindow',

    rest: 'rh.pvf.absence.absence.Restful',

    width: 650,



    getEmployeeField: function () {
        if (!this._employeeField)
            this._employeeField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Servidor',
                name: 'employee',
                rest: 'rh.employee.Restful',
                gridColumnAction: false
            });

        return this._employeeField;
    },

    getStartDateField: function () {
        if (!this._startDateField) {
            this._startDateField = new Ext.form.DateField({
                fieldLabel: 'Data Início',
                format: 'd/m/Y',
                width: 120,
                name:"start_date",
                enableKeyEvents: true,
            });
        }
        return this._startDateField;
    },

    getEndDateField: function () {
        if (!this._endDateField) {
            this._endDateField = new Ext.form.DateField({
                fieldLabel: 'Data Término',
                format: 'd/m/Y',
                width: 120,
                name:"end_date",
                enableKeyEvents: true,
            });
        }
        return this._endDateField;
    },

    getDaysField: function (cfg) {
        if (!this._daysField)
            this._daysField = Ext._create('Ext.form.NumberField', {
                fieldLabel: 'Qtd de Dias',
                name: 'days',
                readOnly: false,
                style: 'text-align:right',
                width: 40
            });

        return this._daysField;
    },

    getObservationField: function (cfg) {
        if (!this._message) {
            this._message = Ext._create('Ext.form.TextArea', {
                anchor: '100%',
                fieldLabel: 'Observação',
                hideLabel: true,
                name: 'observation',
                allowBlank: false
            });
        }
        return this._message;
    },

    getGeneralInfoFieldSet: function (cfg) {
        if (!this._generalInfo)
            this._generalInfo = Ext._create('Ext.form.FieldSet', {
                title: 'Informações Gerais',
                // hidden: cfg.action == "create" ? false : true,
                items: [
                    this.getEmployeeField(cfg),
                ]
            });

        return this._generalInfo;
    },

    getDatesFieldSet: function(cfg){
        if (!this._datesFieldSet){
            this._datesFieldSet = Ext._create('Ext.form.FieldSet', {
                title: 'Informe as datas',
                items: [
                    this.getStartDateField(),
                    this.getEndDateField(),
                ]
            });
        }

        return this._datesFieldSet;
    },
    getObservationFieldSet: function (cfg) {
        if (!this._observation)
            this._observation = Ext._create('Ext.form.FieldSet', {
                title: 'Observação',
                // hidden: cfg.action == "create" ? false : true,
                items: [
                    this.getObservationField(cfg),
                ]
            });

        return this._observation;
    },

    getFormItems: function (cfg) {
        return [
            this.getGeneralInfoFieldSet(),
            this.getDatesFieldSet(),
            this.getObservationFieldSet()
        ];
    },

    

});


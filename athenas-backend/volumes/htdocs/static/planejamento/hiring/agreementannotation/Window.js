Ext._define('planning.hiring.agreementannotation.Window', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.agreementannotation.Restful',

    width: 850,

    getFormPanel: function(cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        width: 715,
                        allowBlank: false,
                        fieldLabel: "Tipo",
                        name: "kind",
                        choiceId: "contrato.ANNOTATION_TYPE",
                        xtype: "choicefield",
                        hiddenName: "kind",
                    },
                    {
                        width: 715,
                        allowBlank: false,
                        fieldLabel: "Data",
                        name: "date",
                        xtype: "datefield",
                    },
                    this.getNote(),
                    this.getSchedule(),
                    this.getScheduleDate(),
                ]
            });

        return this._formPanel;
    },

    getNote: function () {
        if (!this._note)
            this._note = Ext._create('toolkit.fields.CKEditor', {
                name: 'note',
                fieldLabel: "Nota",
                width: 715,
                height: 400
            });

        return this._note;
    },

    getSchedule: function() {
        if (!this._schedule)
            this._schedule = Ext._create('Ext.form.Checkbox', {
                name: 'schedule',
                fieldLabel: 'Agendar Data ?',
                width: 715,
                enableKeyEvents: true,
                listeners: {
                    scope: this,
                    check: function(box, checked) {
                        if(checked) {
                            this.getScheduleDate().setReadOnly(false);
                        }
                        else {
                            this.getScheduleDate().setValue('');
                            this.getScheduleDate().setReadOnly(true);
                        }
                    }                       
                },
            });

        return this._schedule;
    },

    getScheduleDate: function () {
        if (!this._schedule_date)
            this._schedule_date = Ext._create('Ext.form.DateField', {
                name: 'schedule_date',
                fieldLabel: "Data Agendamento",
                width: 715,
            });
        return this._schedule_date;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        this.getScheduleDate().setReadOnly(true);

        planning.hiring.agreementannotation.Window.superclass.constructor.call(this, cfg);
    },
});

Ext._define('planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerWindow', {
    extend: 'planning.hiring.minutesolicitation.MinuteSolicitationWindow',

    height: 500,
    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerWindow.superclass.getFormPanel.call(this);
            this._formPanel.insert(0, {
                items: [
                    {

                        layout: 'column',
                        items: [
                            {
                                columnWidth: '0.3',
                                layout: 'form',
                                items: [
                                    this.getMinute(cfg),
                                ],
                            },
                            {
                                columnWidth: '0.7',
                                layout: 'form',
                                items: [
                                    this.displayMinuteObject(cfg),
                                ],
                            },
                        ]
                    }
                ],
            });
        }

        return this._formPanel;
    },

    getMinute: function () {
        if (!this._getMinute) {
            this._getMinute = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: "Ata",
                allowBlank: false,
                rest: "planning.hiring.minute.MinuteRestful",
                name: "minute",
                anchor: '90%',
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar: ['add', 'edit', 'finalize', 'report', 'export', '-', 'download'],
                    preFilter: [
                        { property: 'status__in', value: [1], stage: 1000 }
                    ]
                },
                comboListeners: {
                    scope: this,
                    changevalid: function (combo, value, oldvalue, valid) {
                        if (valid) {
                            this.params.minute = value
                            this.displayMinuteObject().setValue(combo.getStore().getById(value).get('minute_object'));
                        }
                    },
                    render: function () {
                        if (this.action === 'update')
                            this.getMinute().disable();
                    },
                    afterrender: function (field) {
                        field.focus(false, 200);
                    }
                }
            });
        }
        return this._getMinute;
    },

    displayMinuteObject: function () {
        if (!this._minuteObject)
            this._minuteObject = Ext._create('Ext.form.DisplayField', {
                fieldLabel: 'Objeto da Ata',
                name: 'minute_object',
                anchor: '90%',

            });
        return this._minuteObject;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function (instance) {
                    this.values.minute = instance.minute;
                    this.solicitation(instance.pk);
                    this.oId = instance.pk;
                    this.action = 'update';
                    this.getMinute().disable();
                }
            }
        });

        planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerWindow.superclass.constructor.call(this, cfg);

        this.solicitation(cfg.oId === undefined ? null : cfg.oId);
    }
});
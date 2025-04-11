
Ext._define('judicial.parts.AuthorizationExternalAccessWindow', {
    extend: 'judicial.PartLawsuitActionWindow',

    rest: 'judicial.parts.AuthorizationExternalAccessRestful',

    width: 800,
    autoCreate: false,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        allowBlank: false,
                        fieldLabel: "Movimento",
                        name: "request_external_access",
                        rest: 'judicial.PartLawsuitRestful',
                        xtype: 'rest-autocompletefield',
                        preFilter: [
                            {property: 'lawsuit', value: cfg.params.lawsuit, stage: 1},
                            {property: 'signed_by__isnull', value: false, stage: 2},
                            {property: 'requestexternalaccess__state__in', value: [1, 2], stage: 3},
                        ],
                        gridConfig: {
                            params: cfg.params,
                            columnAction: false,
                            configOrderToolBar: ['search'],
                        }
                    },
                    {   
                        xtype: "combo",
                        fieldLabel: "Decisão",
                        allowBlank: false,
                        lazyRender: true,
                        hiddenName: "state",
                        mode: "local",
                        triggerAction: "all",
                        store: [
                            [1, "Autorizar"],
                            [2, "Revogar"],
                            [3, "Negar"]
                        ],
                        name: "other_lawsuit"
                    },
                    {
                        xtype: 'container',
                        border: false,
                        items: [
                            {
                                allowBlank: false,
                                height: 400,
                                name: "justification",
                                xtype: "ckeditor"
                            }
                        ]
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            buttonAlign: 'left',
            border: false,
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    
                    this.getFormPanel().getForm().setValues(instance);
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        judicial.parts.AuthorizationExternalAccessWindow.superclass.constructor.call(this, cfg);

    }
});

judicial.PartLawsuitGrid.register('judicial.authorizationexternalaccess', 'judicial.parts.AuthorizationExternalAccessWindow');

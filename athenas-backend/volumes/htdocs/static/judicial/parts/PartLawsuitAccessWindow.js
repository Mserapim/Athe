/**
 *
 **/
Ext._define('judicial.parts.PartLawsuitAccessWindow', {
    extend: 'core.RestfulWindow',

    rest: 'judicial.parts.PartLawsuitAccessRestful',

    width: 750,

    getAccessPersonGrid: function(cfg) {
        if(!this._accessPersonGrid)
            this._accessPersonGrid = Ext._create('judicial.parts.PersonHasAccessGrid', {
                title: 'Pessoas Autorizadas',
                gridAutoLoad: false,
                columnAction: false
            });

        return this._accessPersonGrid;
    },

    getAttachmentPanel: function(cfg) {
        if(!this._attachmentPanel)
            this._attachmentPanel = Ext._create('judicial.parts.AttachedGrid', {
                title: 'Anexos',
                gridAutoLoad: false
            });

        return this._attachmentPanel;
    },

    getMainPanel: function(cfg) {
        if(!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel', {
                title: 'Principal',
                layout: 'form',
                border: false,
                frame: true,
                items: [
                    {
                        xtype: "choicefield",
                        fieldLabel: "Motivação",
                        allowBlank: true,
                        hiddenName: "motivation",
                        choiceId: 'judicial.PARTLAWSUIT_ACCESS_MOTIVATION',
                        name: "motivation",
                        width: 615
                    },
                    {
                        xtype: 'container',
                        items: [
                            {
                                allowBlank: false,
                                name: "justification",
                                xtype: "ckeditor",
                                height: 405
                            }
                        ]
                    }
                ]
            });

        return this._mainPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    {
                        xtype: 'tabpanel',
                        activeTab: 0,
                        border: false,
                        height: 580,
                        items: [
                            this.getMainPanel(cfg),
                            this.getAccessPersonGrid(cfg),
                            this.getAttachmentPanel(cfg)
                        ]
                    }
                ]
            });

        return this._formPanel;
    },

    objectId: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._objectId = value;

            if(dispatch)
                this.observeObjectId();
        }

        return this._objectId;
    },

    readAccess: function(value) {
        var rest = this.factoryRestful();

        rest.get(
            value,
            {
                success: {
                    scope: this,
                    fn: function(inst) {
                        this.getSignButton().setDisabled(inst.signed_by !== null);
                        this.getSuspendButton().setDisabled(
                            ((inst.signed_by === null) || !(inst.signed_by !== null && inst.suspended_by === null))
                        );
                    }
                },
                failure: {
                    scope: this,
                    fn: function(err) {
                        this.getSignButton().disable();
                        this.getSuspendButton().disable();
                    }
                }
            },
            {
                el: this.getEl(),
                msg: 'checando condições...'
            }
        );
    },

    observeObjectId: function() {
        var value = this.objectId();

        if(value) {
            this.getAttachmentPanel().enable();
            this.getAttachmentPanel().setParam('attached_part_access', value);
            this.getAttachmentPanel().setFilterProperty('attached_part_access', value, 100);

            this.getAccessPersonGrid().enable();
            this.getAccessPersonGrid().setParam('access', value);
            this.getAccessPersonGrid().setFilterProperty('access', value, 100);

            this.readAccess(value);
        }
        else {
            this.getAttachmentPanel().disable();
            this.getAttachmentPanel().setParam('attached_part_access', value);
            this.getAttachmentPanel().setFilterProperty('attached_part_access', value, 100, false);
            this.getAttachmentPanel().getStore().removeAll();

            this.getAccessPersonGrid().disable();
            this.getAccessPersonGrid().setParam('access', value);
            this.getAccessPersonGrid().setFilterProperty('access', value, 100, false);
            this.getAccessPersonGrid().getStore().removeAll();
        }
    },

    sign: function() {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'assinando...'});
        var me = this;
        
        mask.show();
        rest.sign(
            this.objectId(),
            {
                scope: this,
                fn: function(rst) {
                    console.log(rst);
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Assinando',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() { mask.hide(); me.close();}
            }
        );
    },

    suspend: function() {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'suspendendo...'});
        
        mask.show();
        rest.suspend(
            this.objectId(),
            {
                scope: this,
                fn: function(rst) {
                    console.log(rst);
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Suspendendo',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() { mask.hide(); }
            }
        );
    },

    getSignButton: function(cfg) {
        if(!this._signButton)
            this._signButton = Ext._create('Ext.Button', {
                text: 'Assinar',
                disabled: true,
                scope: this,
                handler: function() { this.sign(); }
            });

        return this._signButton;
    },

    getSuspendButton: function(cfg) {
        if(!this._suspendButton)
            this._suspendButton = Ext._create('Ext.Button', {
                text: 'Suspender',
                disabled: true,
                scope: this,
                handler: function() { this.suspend(); }
            });

        return this._suspendButton;
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                this.getSignButton(cfg),
                this.getSuspendButton(cfg),
                '->',
            ].concat(judicial.parts.PartLawsuitAccessWindow.superclass.getButtons.call(this, cfg));

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                buttonAlign: 'left',
                saveAndContinue: {
                    scope: this,
                    fn: function(instance) {
                        this.objectId(instance.pk);

                        this.getFormPanel().getForm().setValues(instance);
                        this.oId = instance.pk;
                        this.action = 'update';
                    }
                },
            }
        );

        judicial.parts.PartLawsuitAccessWindow.superclass.constructor.call(this, cfg);
        this.objectId(cfg.oId || null);
    }
});

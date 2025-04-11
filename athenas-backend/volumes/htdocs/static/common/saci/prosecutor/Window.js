
Ext._define('common.saci.prosecutor.Window', {
    extend: 'common.saci.attendance.Window',

    rest: 'common.saci.prosecutor.Restful',

    step: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._step = value;

            if(dispatch)
                this.observerStep();
        }

        return this._step;
    },

    observerStep: function() {
        var value = this.step();

        if(value) {
            var rest = Ext._create('common.saci.step.Restful');
            var mask = new Ext.LoadMask(this.getForwardTilePanel().getEl(), {msg: 'buscando documento...'});
            mask.show();
            rest.rendererDocument(
                value,
                {
                    scope: this,
                    fn: function(document) {
                        this.getForwardTilePanel().enable();
                        this.getForwardTilePanel().setPageContent(document.content);
                    }
                },
                {
                    fn: function(message) {
                        Ext.Msg.show({
                            title: 'Buscando documento',
                            msg: message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                {fn: function() {mask.hide();}}
            );

        }
        else {
            this.getForwardTilePanel().disable();
            this.getForwardTilePanel().setPageContent('');
        }
    },

    observeAttendance: function() {
        var value = this.attendance();

        this.changeButtons(value);
        this.loadAttachment(value);

        this._observerAttendaceValue(value);
    },

    _observerAttendaceValue: function(value){
        if(value) {
            this.getExtrajudicialButton().enable();
            this.getForwardPanel().enable();

            this.getStepGrid().setFilterProperty('attendance', value, 100);
        } else {
            this.getExtrajudicialButton().disable();
            this.getForwardPanel().disable();

            this.getStepGrid().setFilterProperty('attendance', 0, 100);

        }
    },

    getTabPanelItems: function(cfg){
        return common.saci.prosecutor.Window.superclass.getTabPanelItems.call(this, cfg).concat([
            this.getForwardPanel(cfg)
        ]);
    },

    getItemsButton: function(cfg){
        return common.saci.prosecutor.Window.superclass.getItemsButton.call(this, cfg).concat([
            this.getExtrajudicialButton(cfg)
        ]);
    },

    openNoticeOfficeWindow: function(){
        var values = (this.newValues || this.values);
        var attendance = this.attendance()
        var wnd = Ext._create('judicial.parts.AssessmentNoticeOfficeWindow', {
            action: 'create',
            modal: true,
            params: {
                location: values.department,
                protocol_origin: values.protocol,
                notice_office_type: 1
            },
            values: {
                notice_title: values.subject,
                notice: values.story,
                interested: values.person,
            },
            callback: {
                success: {
                    scope: this,
                    fn: function(instance) {
                        core.invokeCallback(this.success || {fn: Ext.emptyFn}, instance);
                        wnd.close();
                        core.invokeCallback((this.callback || {}).success);
                        this.close();
                        this.afterGenerateLawsuit(attendance, instance.pk);
                    }
                }
            }
        }).show();
    },

    afterGenerateLawsuit: function(attendance, part) {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'atualizando Atendimento...'});
        var values = {};

        values.attendance = attendance;
        values.part = part;

        rest.afterGenerateLawsuit(
            values,
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Atendimento',
                        msg: 'Foi gerado uma notícia de fato. Acesse seu gestor de processo no E-Ext.',
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Atendimento',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {fn: function() {mask.hide();}}
        );
    },

    makeNoticeOfficeWindow: function() {
        var rest = this.factoryRestful();

        rest.checkToSign(
            this.oId,
            {
                scope: this,
                fn: function(document) {
                    this.openNoticeOfficeWindow();
                }
            },
            {
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Atendimento',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {fn: function() {}}
        );
    },

    getExtrajudicialButton: function(cfg) {
        if(!this._extrajudicialButton)
            this._extrajudicialButton = Ext._create('Ext.Button', {
                text: 'Gerar Notícia de Fato',
                scope: this,
                disabled: true,
                handler: this.makeNoticeOfficeWindow
            });

        return this._extrajudicialButton;
    },

    getForwardTilePanel: function() {
        if(!this._feedbackTilePanel)
            this._feedbackTilePanel = Ext._create('core.TilePagePanel', {
                disabled: true,
                height: 300,
                minHeight: 300,
                region: 'center'
            });

        return this._feedbackTilePanel;
    },

    getStepGrid: function() {
        if(!this._stepGrid) {
            this._stepGrid = Ext._create('common.saci.step.Grid', {
                configOrderToolBar: [],
                region: 'north',
                split: true,
                scope: this,
                height: 200,
                minHeight: 150,
                columnAction: false,
                gridAutoLoad: false,
                doubleClickHandler: function(){}
            });

            this._stepGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();
                    if(selection.length > 0)
                        this.step(selection[0].get('pk'));
                    else
                        this.step(null);
                }
            });
        }
        return this._stepGrid;
    },

    getForwardPanel: function(cfg){
        if(!this._forwardTab)
            this._forwardTab = Ext._create('Ext.Panel',{
                layout: 'border',
                title: 'Encaminhamentos',
                border: false,
                scope: this,
                height: 600,
                disabled: true,
                items: [
                    this.getStepGrid(),
                    this.getForwardTilePanel()
                ]
            });
        return this._forwardTab;
    },

    forward: function() {
        Ext._create('common.saci.prosecutor.ForwardInternalWindow', {
            action: 'create',
            modal: true,
            oId: this.attendance(),
            params: {
                department: this.getDepartmentField().getValue(),
                prosecutor: true
            },
            callback: {
                success: {
                    scope: this,
                    fn: function(instance) {
                        core.invokeCallback((this.callback || {}).success);
                        this.close();
                    }
                }
            }
        }).show();
    },

    finalize: function() {
        Ext._create('common.saci.prosecutor.FinalizeWindow', {
            action: 'create',
            modal: true,
            oId: this.attendance(),
            params: {
                department: this.getDepartmentField().getValue(),
                prosecutor: true
            },
            callback: {
                success: {
                    scope: this,
                    fn: function(instance) {
                        core.invokeCallback((this.callback || {}).success);
                        this.close();
                    }
                }
            }
        }).show();
    },

    forwardExternal: function() {
        Ext._create('common.saci.prosecutor.ForwardExternalWindow', {
            action: 'create',
            modal: true,
            oId: this.attendance(),
            params: {
                department: this.getDepartmentField().getValue(),
                prosecutor: true
            },
            callback: {
                success: {
                    scope: this,
                    fn: function(instance) {
                        core.invokeCallback((this.callback || {}).success);
                        this.close();
                    }
                }
            }
        }).show();
    },

});

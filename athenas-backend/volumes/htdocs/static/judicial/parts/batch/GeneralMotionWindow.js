Ext._define('judicial.parts.batch.GeneralMotionWindow', {
    extend: 'judicial.parts.GeneralMotionWindow',

    getAttachementPanel: function (cfg) {
        if (!this._attachmentPanel)
            this._attachmentPanel = Ext._create('judicial.parts.batch.AttachedGrid', {
                title: 'Anexos',
                gridAutoLoad: false
            });

        return this._attachmentPanel;
    },

    getScientifyWorkplaceGrid: function (cfg) {
        if (!this._scientifyWorkplaceGrid)
            this._scientifyWorkplaceGrid = Ext._create('judicial.parts.batch.ScientifyWorkplaceGrid', {
                title: 'Comunicações',
                gridAutoLoad: false,
                columnAction: false
            });

        return this._scientifyWorkplaceGrid;
    },

    signBatch: function (parameters) {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Assinando procedimentos...' });

        mask.show();

        Ext.Ajax.request({
            url: core.callAction('EJudGeneralMotion', 'sign_batch'),
            params: parameters,
            method: 'POST',
            scope: this,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var rst = Ext.decode(xhr.responseText);

                if (rst.success) {
                    this.destroy();
                    Ext.Msg.show({
                        title: 'Movimentação de procedimentos em bloco',
                        msg: rst.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                }
                else
                    Ext.Msg.show({
                        title: 'Erro na movimentação de procedimentos em bloco',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function () {
                Ext.Msg.show({
                    title: 'Falha',
                    msg: 'Falha na movimentação. Nenhum procedimento foi finalizado.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    saveBatch: function (parameters) {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Salvando documento nos procedimentos...' });

        mask.show();

        Ext.Ajax.request({
            url: core.callAction('EJudGeneralMotion', 'save_batch'),
            params: parameters,
            method: 'POST',
            scope: this,
            callback: function () {
                mask.hide();
            },
            success: function (xhr) {
                var rst = Ext.decode(xhr.responseText);

                if (rst.success) {
                    this.readDataCallback(rst.parts);
                    // this.destroy();
                    Ext.Msg.show({
                        title: 'Movimentação de procedimentos em bloco',
                        msg: rst.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                }
                else
                    Ext.Msg.show({
                        title: 'Erro na movimentação de procedimentos em bloco',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function () {
                Ext.Msg.show({
                    title: 'Falha',
                    msg: 'Falha na movimentação. Nenhum procedimento foi modificado.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    generalMotionInstances: function (value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if (value !== undefined) {
            this._generalMotionInstance = value;

            if (dispatch) this.observerGeneralMotion();
        }

        return this._generalMotionInstance;
    },

    observerGeneralMotion: function () {
        var value = this.generalMotionInstances();

        if (value) {
            this.getAttachementPanel().enable();
            this.getAttachementPanel().setParam('attached_documents', value);
            this.getAttachementPanel().setFilterProperty('attached_document__in', value, 1000);

            this.getScientifyWorkplaceGrid().enable();
            this.getScientifyWorkplaceGrid().setParam('parts', value);
            this.getScientifyWorkplaceGrid().setFilterProperty('part__in', value, 1001);
        }
        else {
            this.getAttachementPanel().disable();
            this.getAttachementPanel().setParam('attached_documents', value);
            this.getAttachementPanel().setFilterProperty('attached_document__in', 0, 1000);
            this.getAttachementPanel().getStore().removeAll();

            this.getScientifyWorkplaceGrid().disable();
            this.getScientifyWorkplaceGrid().setParam('parts', 0);
            this.getScientifyWorkplaceGrid().setFilterProperty('part__in', 0, 1001, false);
            this.getScientifyWorkplaceGrid().getStore().removeAll();
        }
    },

    readDataCallback: function (parts) {
        this.generalMotionInstances(parts);
    },

    getLeftButtons: function (cfg) {
        if (!this._leftButtons)
            this._leftButtons = [
                {
                    text: 'Assinar (bloco) ',
                    scope: this,
                    handler: function(){
                        params = Ext.applyIf(
                            this.getFormPanel().getForm().getValues(),
                            this.getParams()
                        )
                        this.signBatch(params);
                    } 
                }
                // ,
                // {
                //     text: 'Pré-análise (bloco)',
                //     scope: this,
                //     handler: this.workerreminder,
                // }
            ];

        return this._leftButtons;
    },

    getRightButtons: function (cfg) {
        if (!this._rightButtons)
            this._rightButtons = [
                {
                    text: 'Salvar (Bloco)',
                    scope: this,
                    handler: function () {
                        params = Ext.applyIf(
                            this.getFormPanel().getForm().getValues(),
                            this.getParams()
                        )
                        this.saveBatch(params); 
                    }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];

        return this._rightButtons;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        judicial.parts.batch.GeneralMotionWindow.superclass.constructor.call(this, cfg);
    }
});

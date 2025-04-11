Ext.ns('toolkit.rh.gfp.paycheck.socialsecurity');

toolkit.rh.gfp.paycheck.socialsecurity.WindowFileGenerator = Ext.extend(
    Ext.Window,
    {
        getFormPanel: function(cfg) {
            if(!this.formPanel)
                this.formPanel = new Ext.form.FormPanel({
                    frame: true,
                    items: [
                         {
                            name: 'sheet',
                            xtype:'hidden',
                            value: cfg.sheet
                        }
                    ]
                });

            return this.formPanel;
        },

        execute: function(){
            var form = this.getFormPanel().getForm();

            form.waitMsgTarget = this.getFormPanel().getEl();
            form.submit({
                url: toolkit.util.Normalize.controller_action(this.controller, this.action),
                failure: function(form, action) {
                    var result = action.result;
                    alert(result.message);
                    this.close();
                },
                success: function(form, action){
                    var result = action.result;
                    alert(result.message);
                    this.close();
                },
                scope: this,
                waitMsg: 'Aguarde ...'
            });
        },

        constructor: function(cfg) {
            if(!cfg) cfg = {}
            Ext.applyIf(
                cfg,
                {
                    title: 'Gerador de arquivos do IGEPREV',
                    closable: true,
                    resizable: false,
                    width: 400,
                    border: false,
                    modal: true,
                    controller: 'GFPSocialSecurityWindowFileGenerator',
                    action: 'start',
                    items: [
                        this.getFormPanel(cfg),
                    ],
                    buttons: [
                        {
                            text: 'Executar',
                            scope: this,
                            handler: this.execute
                        },
                        {
                            text: 'Cancelar',
                            scope: this,
                            handler: this.destroy
                        }
                    ]
                }
            );

            toolkit.rh.gfp.paycheck.socialsecurity.WindowFileGenerator.superclass.constructor.call(this, cfg);
        }         
    }
);
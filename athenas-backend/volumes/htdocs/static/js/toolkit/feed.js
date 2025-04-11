
if(typeof(toolkit) != "undefiend") {

    toolkit.feed = {}
    toolkit.feed.Widget = function() {}

    toolkit.feed.Widget.prototype = {

        show: function() {

            this.form = new Ext.Panel({
                height: 100,
                border: false,
                items: new Ext.FormPanel({
                    border: false,
                    labelWidth: 120,
                    width: 485,
                    style: {
                        margin: "15pt auto"
                    },
                    items: [
                        {
                            fieldLabel: "Endereço do Feed",
                            xtype: "field",
                            name: "Url",
                            width: 350
                        }
                    ],
                    buttonAlign: "center",
                    buttons: [
                        {
                            text: "Adicionar"
                        }
                    ]
                })
            });

            this.stPanel = new Ext.Toolbar.TextItem({
                text: "Testando",
                style: {
                    border: "1px inset #bfb",
                    width: "100%"
                }
            });

            this.feeds = new Ext.Panel({
                height: 100,
                layout: "fit",
                style: {
                    "margin-top": "5pt"
                },
                items: [
                    new Ext.Panel({
                        layout: "accordeon",
                        height: 100,
                        items: [
                            {
                                xtype: "panel",
                                title: "test"
                            },
                            {
                                xtype: "panel",
                                title: "test"
                            }
                        ]
                    })
                ],
                bbar: [
                    this.stPanel
                ]
            });

            this.stPanel.on(
                "render",
                function() {
                    this.stPanel.setWidth(this.stPanel.ownerCt.getBox().width - 2)
                    console.debug(this.stPanel.ownerCt.getBox());
                },
                this
            );

            this.panel = new Ext.Panel({
                title: "Test",
                style: 'padding: 5pt 10pt  5pt 5pt',
                items:  [
                    this.form,
                    this.feeds
                ]
            });

            this.feeds.on(
                "render",
                function() {
                    this.feeds.setHeight(screen.height - 382);
                    console.debug(this.form.getBox());
                },
                this
            )

            toolkit.Application.tabspace.remove(toolkit.Application.tabspace.getActiveTab());
            toolkit.Application.tabspace.add(this.panel);
            toolkit.Application.tabspace.setActiveTab(this.panel);

            toolkit.Application.tabspace.doLayout();

        }

    }

}